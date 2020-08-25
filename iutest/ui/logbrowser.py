from iutest.qt import QtCore, QtGui, QtWidgets, Signal
from iutest.core import gotocode
from iutest.ui import uiconstants
from iutest.ui import uiutils
from iutest.ui import scrollareapan


class LogBrowser(QtWidgets.QTextBrowser):
    searchNeeded = Signal(str)

    def __init__(self, parent=None):
        QtWidgets.QTextBrowser.__init__(self, parent)
        self._pan = scrollareapan.ScrollAreaPan(self.viewport(), self.horizontalScrollBar(), self.verticalScrollBar())
        
        self._codeVisitor = gotocode.CodeLineVisitor(self)
        self._codeVisitor.errorIssued.connect(self._onGoToCodeError)
        self._setupUi()

    def _setupUi(self):
        fn = self.font()
        pixelSize = max(12, fn.pixelSize() + 2)
        fn.setPixelSize(pixelSize)
        fn.setFamily("Courier New")
        self.setFont(fn)
        self.setReadOnly(True)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.onLinkClicked)
        self.setToolTip("The test logging browser, use <b>MMB</b> to pan around.")
        self._initCSS()

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
        self.horizontalScrollBar().setValue(0)

    def onLinkClicked(self, url):
        path, _, line = url.query().rpartition("=")
        if not path:
            return
        if not line:
            line = 0
        self._codeVisitor.goTo(path, line)

    def logSeparator(self,):
        sep = ">" * 70
        self.logWarning("<br>{}<br>".format(sep))

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

    def _onGoToCodeError(self, msg):
        uiutils.popUpMessageOnCursorPos(msg, self)

    def keyPressEvent(self, event):
        key = event.key()
        ctrl = bool(event.modifiers() & QtCore.Qt.ControlModifier)
        if ctrl and key == QtCore.Qt.Key_F:
            self.searchNeeded.emit(str(self.textCursor().selectedText()))
            event.accept()
            return

        QtWidgets.QTextBrowser.keyPressEvent(self, event)
