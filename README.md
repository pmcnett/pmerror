pmerror
=======

Graphical unhandled exception handler for Dabo applications.

It will catch unhandled errors, display a friendly UI dialog to the end-user, and log the error to an XML file in the user Application Directory.

Requirements
------------

* Python 2.6.5 or higher
* wxPython 2.8.12.1 or higher
* Dabo 0.9.4 or higher


Screenshots
-----------
* <a href="https://raw.github.com/pmcnett/pmerror/master/screenshot_mac.png">Mac</a>


Run the demo
------------

After installing and confirming the above prerequisites were installed:

    cd pmerror
    python app.py


Use it in your application
--------------------------

Put it in your PYTHONPATH. I have the pmerror package under /home/pmcnett/pmerror and so I add a .pth file to my `/usr/local/lib/python2.6/dist-packages` directory that says `/home/pmcnett/pmerror`.

Then mix it in to your application like:

```python
import dabo.ui
dabo.ui.loadUI("wx")
from dabo.dApp import dApp
from pmerror.app import ErrorAppMixin

class ErrorHandlingApp(dApp, ErrorAppMixin): pass

app = ErrorHandlingApp(MainFormClass=None)
app.HandleErrors = True
```
