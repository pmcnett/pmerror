# -*- coding: utf-8 -*-

import sys
import os
import copy
import platform
import time
import datetime
import traceback
import dabo.ui
from dabo.lib.utils import getUserAppDataDirectory

__all__ = ["ErrorAppMixin"]

default_error_log_spec = \
"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>

<error_log_entry>

    <timestamp>%(timestamp)s</timestamp>
    <app_name>%(app_name)s</app_name>
    <app_version>%(app_version)s</app_version>
    <app_license>%(app_license)s</app_license>
    <platform>%(platform)s</platform>
    <exc_type>%(exc_type)s</exc_type>
    <exc_obj>%(exc_obj)s</exc_obj>

    <active_form>%(active_form)s</active_form>
    <active_control>%(active_control)s</active_control>

    <tb_msg>%(tb_msg)s</tb_msg>

    <last_callafter_stack>%(last_callafter_stack)s</last_callafter_stack>

    <user_notes>%(user_notes)s</user_notes>

</error_log_entry>
"""


def esc_xml(val):
    if not isinstance(val, basestring):
        val = str(val)
    val = val.replace('&', '&amp;')
    val = val.replace('<', '&lt;')
    val = val.replace('>', '&gt;')
    return val


class ErrorAppMixin(object):
    """
    Application mixin that automatically logs unhandled exceptions.

    The user will be prompted to enter additional information, and the 
    application will close. The error will appear as a file in the user's 
    application data directory for this application in XML format.

    Mix-in to your dApp subclass. Example:
        from dabo.dApp import dApp
        from pmerror.app import ErrorAppMixin
        class MyApp(dApp, ErrorAppMixin): pass

    Your application can then determine what to do with these XML
    error files. A common thing to do is email them as they happen to
    the developer(s) of the application and then delete them locally.
    """

    def initProperties(self):
        ## The default is to handle errors when we are distributed to the 
        ## end-user via py2exe, py2app, cxFreeze, PyInstaller, etc. but
        ## to not handle errors otherwise (like at development time).
        self.PMError_HandleErrors = hasattr(sys, "frozen")
        super(AppMixin, self).initProperties()

    def logError(self, error_data):
        """Log the error in an XML file inside the user's AppData directory."""
        app_data_dir = getUserAppDataDirectory(self.getAppInfo("appShortName"))
        spec = self.PMError_LogSpec
        for k, v in error_data.items():
            error_data[k] = esc_xml(v)
        xml = spec % error_data
        filename = "error_%s.entry" % time.time()
        open(os.path.join(getUserAppDataDirectory(self.getAppInfo("appShortName")),
                          filename), "wb").write(xml)
        print app_data_dir

    def beforeHandleError(self, error_data):
        """
        Subclass hook.

        Override if you want to take action before the default action happens.
        If you want to keep the default action from happening (ignoring the
        error completely(!)), return anything but None.

        A typical use for modifying the error_data  would be to fill in the 
        appLicense field.
        """
        pass

    def afterHandleError(self, error_data):
        """
        Subclass hook.

        Override if you want to take some additional action after the default
        action of writing the xml error log has happened and before the
        application exits. Return anything but None to stop the application
        from quitting (not recommended).
        """
        pass
 
    def handleError(self, exc_type, exc_obj, exc_tb):
        """
        Handle the error.
        
        Display a dialog to the user giving some information and allowing them
        to enter some notes about what they were doing. Then log the error to 
        an XML file in their AppData directory, and close the application.
        """
        ## If something goes wrong in the error handling code, don't trap it
        ## with the buggy code again but allow the default excepthook to run.
        sys.excepthook = sys.__excepthook__
        af = self.ActiveForm
        ac = af.ActiveControl if af else None
        error_data = {"timestamp": datetime.datetime.utcnow(),
                      "platform": platform.platform(),
                      "app_name": self.getAppInfo("appName"),
                      "app_version": self.getAppInfo("appVersion"),
                      "app_license": "",  ## subclasses to fill in before hook
                      "active_form": str(af),
                      "active_control": str(ac),
                      "exc_type": exc_type,
                      "exc_classname": exc_type.__name__,
                      "exc_obj": exc_obj,
                      "tb_msg": ''.join(traceback.format_exception(
                                        exc_type, exc_obj, exc_tb)).strip(),
                      "last_callafter_stack": getattr(dabo.ui, "lastCallAfterStack", "")}

        if self.beforeHandleError(error_data) is not None:
            # Running event loop will continue in unknown state.
            return

        user_error_data = copy.copy(error_data)
        if not self.PMError_ShowTracebackToUser:
            user_error_data["tb_msg"] = ""
        dlg = self.PMError_DialogClass(ErrorData=user_error_data)
        dlg.show()
        error_data["user_notes"] = dlg.edtUserNotes.Value.strip()
        del(dlg)

        self.logError(copy.copy(error_data))
        if self.afterHandleError(error_data) is not None:
            # Running event loop will continue in unknown state.
            return
        sys.exit()

    def _getErrorDialogClass(self):
        ret = getattr(self, "_error_dialog_class", None)
        if ret is None:
            from ui import ErrorDialog
            return ErrorDialog
        return ret

    def _setErrorDialogClass(self, val):
        self._error_dialog_class = val

    def _getErrorLogSpec(self):
        return getattr(self, "_error_log_spec", default_error_log_spec)

    def _setErrorLogSpec(self, val):
        self._error_log_spec = val

    def _getHandleErrors(self):
        return getattr(self, "_handle_errors", False)

    def _setHandleErrors(self, handle_errors):
        self._handle_errors = handle_errors
        if handle_errors:
            sys.excepthook = self.handleError
        else:
            sys.excepthook = sys.__excepthook__

    def _getShowTB(self):
        return getattr(self, "_show_tb", False)

    def _setShowTB(self, val):
        self._show_tb = val

    PMError_DialogClass = property(_getErrorDialogClass, _setErrorDialogClass,
        None, """Specifies the dialog class to use. (ui.ErrorDialog)""")

    PMError_LogSpec = property(_getErrorLogSpec, _setErrorLogSpec, None, 
        """Specifies the format of the XML error log entry.""")

    PMError_HandleErrors = property(_getHandleErrors, _setHandleErrors, None,
        """Specifies whether the error is handled here or not.""")

    PMError_ShowTracebackToUser = property(_getShowTB, _setShowTB, None,
        """Specifies whether the traceback is shown in the dialog (False).""")


if __name__ == "__main__":
    dabo.ui.loadUI("wx")
    from dabo.dApp import dApp
    class TestApp(dApp, ErrorAppMixin): pass
    testApp = TestApp(MainFormClass=None)
    testApp.setup()
    h = testApp.PMError_HandleErrors = dabo.ui.areYouSure("Set to handle errors?")
    if h is None:
        sys.exit("test canceled.")
    h = testApp.PMError_ShowTracebackToUser = dabo.ui.areYouSure("Show traceback to user?")
    if h is None:
        sys.exit("test canceled.")
    1/0

