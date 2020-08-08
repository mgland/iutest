from iutest.qt import QtCore, QtWidgets, Signal

class RootPathEdit(QtWidgets.QLineEdit):
    rootPathChanged = Signal(str, str)

    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)
        self.editingFinished.connect(self.onEditFinished)
        self._initPath = None

    def setInitialPath(self, path):
        self._initPath = path

    def setText(self, txt):
        QtWidgets.QLineEdit.setText(self, txt)
        self.setInitialPath(txt)

    def onEditFinished(self):
        txt = self.text()
        if txt == self._initPath:
            return

        self.setInitialPath(txt)
        self.rootPathChanged.emit(txt, "")
