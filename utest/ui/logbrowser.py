from utest.ui import uiconstants
from utest.core import uistream
from utest.qt import QtCore, QtGui, QtWidgets


class LogBrowser(QtWidgets.QTextBrowser):
    def __init__(self, parent=None):
        QtWidgets.QTextBrowser.__init__(self, parent)
        fn = self.font()
        pixelSize = max(12, fn.pixelSize() + 2)
        fn.setPixelSize(pixelSize)
        fn.setFamily("Courier New")
        self.setFont(fn)
        self.setReadOnly(True)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.onLinkClicked)
        self._initCSS()

        self.process = QtCore.QProcess(self)

    def _initCSS(self):
        css = """
        a:link {
            color: #C8C8C8;
        }

        * {
            white-space: pre;
        }
        """
        # text-decoration: none;
        self.document().setDefaultStyleSheet(css)

    def logWithColor(self, msg, color, *args):
        self.moveCursor(QtGui.QTextCursor.End)
        # SELF.setTextColor(color)
        msg = msg if not args else (msg % args)
        msg = "<font color=%s>%s</font>" % (color.name(), msg)
        self.insertHtml(msg)
        self.moveCursor(QtGui.QTextCursor.End)

    def onLinkClicked(self, url):
        path, _, line = url.query().rpartition("=")
        if not path:
            return
        if not line:
            line = 0
        self.browseSourceFileOnLine(path, line)

    def browseSourceFileOnLine(self, filePath, line=0):
        # program = "D:/Programs/Microsoft VS Code/Code.exe"
        program = "code"
        target = ":".join([filePath, line])
        arguments = ["--goto", target]
        self.process.start(program, arguments)

    def logSeparator(self,):
        sep = ">" * 70
        self.logInformation("<br>{}<br>".format(sep))

    def logInformation(self, msg, *args):
        self.logWithColor(msg, uiconstants.LOG_COLOR_INFORMATION, *args)

    def logSuccess(self, msg, *args):
        self.logWithColor(msg, uiconstants.LOG_COLOR_SUCCESS, *args)

    def logFailed(self, msg, *args):
        self.logWithColor(msg, uiconstants.LOG_COLOR_FAILED, *args)

    def logError(self, msg, *args):
        self.logWithColor(msg, uiconstants.LOG_COLOR_ERROR, *args)

    def logWarning(self, msg, *args):
        self.logWithColor(msg, uiconstants.LOG_COLOR_WARNING, *args)

    def closeEvent(self, event):
        uistream.UiStream.deregister(self)
        QtWidgets.QTextBrowser.closeEvent(self, event)

    def onTestStart(self):
        uistream.UiStream.register(self)
