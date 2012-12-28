import dabo
if __name__ == "__main__":
    import dabo.ui
    dabo.ui.loadUI("wx")

__all__ = ["ErrorDialog"]

class ErrorDialog(dabo.ui.dDialog):
    def initProperties(self):
        self.Caption = "Error in %s" % self.Application.getAppInfo("appName")
        self.ShowCloseButton = False
        self.AutoSize = False
        self.Centered = True
        self.ShowSystemMenu = False
        self.ReleaseOnEscape = False
        self.Size = (600, 450)

    def addControls(self):
        b1 = 10
        vs = self.Sizer = dabo.ui.dSizer("v")
        txt = """
<body bgcolor="#cccccc">
<h3>Please do not be alarmed.</h3>

<p>We are sorry, an error has occurred that we don't know how to handle. 
The error has been logged for review, and the details are shown below.
Please feel free to add any additional information that may help us 
diagnose the issue. If you keep having trouble please contact us for
help. When you click 'close', the application will exit. Thank you.</p>

<hr />

<b>Time:</b> %(timestamp)s<br />
<b>Platform Info:</b> %(platform)s<br />
<b>Application Name:</b> %(app_name)s<br />
<b>Application Version:</b> %(app_version)s<br />
<b>Error Class:</b> %(exc_classname)s<br />

<font size=-2 color="#0000a0">
<pre>%(tb_msg)s</pre>
</font>

</body>
""" % self.ErrorData

        self.edtIntroText = dabo.ui.dHtmlBox(self, Value=txt, Height=200,
                BackColor=self.BackColor)
        vs.append(self.edtIntroText, 1, "expand", border=b1)

        hs = dabo.ui.dSizer("h")
        hs.append(dabo.ui.dLabel(self, FontSize=7, Caption="Your notes:"))
        hs.append(dabo.ui.dEditBox(self, FontSize=8, Name="edtUserNotes"), 1)
        hs.appendSpacer((10,0))
        hs.append(dabo.ui.dButton(self, Caption="Close", OnHit=self.onHit_btnClose, CancelButton=True))
        vs.append(hs, "expand", border=b1, alignment="right")
        self.edtUserNotes.setFocus()

    def onHit_btnClose(self, evt):
        self.hide()

    def _getErrorData(self):
        return getattr(self, "_error_data", {})

    def _setErrorData(self, val):
        assert isinstance(val, dict)
        self._error_data = val

    ErrorData = property(_getErrorData, _setErrorData, None,
            """Specifies the error data dictionary to use.""")


if __name__ == "__main__":
    import sys
    import traceback
    import platform
    import datetime
    from dabo.dApp import dApp
    def errorHandler(exc_type, exc_obj, exc_tb):
        print str(exc_type)
        tb_msg = ''.join(traceback.format_exception(exc_type, exc_obj, exc_tb))
        error_data = {"timestamp": datetime.datetime.utcnow(),
                      "platform": platform.platform(),
                      "app_name": "Test of ErrorDialog",
                      "app_version": "v0.5",
                      "exc_type": exc_type,
                      "exc_classname": exc_type.__name__,
                      "exc_obj": exc_obj,
                      "tb_msg": ''.join(traceback.format_exception(
                                        exc_type, exc_obj, exc_tb)).strip()}
        frm = ErrorDialog(ErrorData=error_data)
        frm.show()
        print frm.edtUserNotes.Value
    sys.excepthook = errorHandler
    app = dApp(MainFormClass=None)
    app.setup()
    1/0
