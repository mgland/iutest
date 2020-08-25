from iutest.qt import QtCore, QtWidgets, Signal

from iutest.core import appsettings
from iutest.core import iconutils
from iutest.ui import uiutils
from iutest.ui import inlinebuttonlineedit as btnLineEdit


class RootPathEdit(btnLineEdit.InlineButtonLineEdit):
    _moreIcon = None
    rootPathChanged = Signal(str, str)

    rootDirPicked = Signal(str)
    topDirPicked = Signal(str)

    saveCurrentDirSettings  = Signal()
    loadSavedDirPair  = Signal(str, str, str)
    deleteCurrentDirSettings  = Signal()

    def __init__(self, parent=None):
        btnLineEdit.InlineButtonLineEdit.__init__(self, withClearButton=False, parent=parent)
        self._initIcons()

        self.editingFinished.connect(self.onEditFinished)
        self._initPath = None
        
        self._browseBtn = uiutils.makeIconButton(self._moreIcon, self)
        self._browseBtn.clicked.connect(self._onBrowseBtnClicked)
        self._browseMenu = QtWidgets.QMenu(self._browseBtn)
        self.addButton("Browse", self._browseBtn)
        self.regenerateBrowseMenu()

    @classmethod
    def _initIcons(cls):
        if cls._moreIcon:
            return

        iconutils.initSingleClassIcon(cls, "_moreIcon", "more.svg")

    def _onBrowseBtnClicked(self):
        btmLeft = self._browseBtn.mapToGlobal(QtCore.QPoint(0, self._browseBtn.height()))
        self._browseMenu.exec_(btmLeft)

    def setInitialPath(self, path):
        self._initPath = path

    def setText(self, txt):
        btnLineEdit.InlineButtonLineEdit.setText(self, txt)
        self.setInitialPath(txt)

    def onEditFinished(self):
        txt = str(self.text())
        if txt == self._initPath:
            return

        self.setInitialPath(txt)
        self.rootPathChanged.emit(txt, "")

    def regenerateBrowseMenu(self):
        self._browseMenu.clear()

        act = self._browseMenu.addAction("Pick Test Root Dir ...")
        act.triggered.connect(self._onBrowseTestsRootDir)
        act = self._browseMenu.addAction("Pick Top Root Dir ...")
        act.triggered.connect(self._onBrowseTopDir)
        self._browseMenu.addSeparator()
        act = self._browseMenu.addAction("Save Current Path Settings ...")
        act.triggered.connect(self.saveCurrentDirSettings)
        act = self._browseMenu.addAction("Delete Current Settings ...")
        act.triggered.connect(self.deleteCurrentDirSettings)
        self._browseMenu.addSeparator()

        # Read settings:
        config = appsettings.get().testDirSettings()
        for key, pair in config.items():
            act = self._browseMenu.addAction(key)
            act.triggered.connect(self._loadSavedDirPair)
            act.setToolTip("\n".join(pair))
        self._browseMenu.addSeparator()

    def _onBrowseTestsRootDir(self):
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Pick the Test Root Directory"
        )
        if dirPath:
            self.rootDirPicked.emit(dirPath)

    def _onBrowseTopDir(self):
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Pick the Top Python Directory"
        )
        if dirPath:
            self.topDirPicked.emit(dirPath)

    def _loadSavedDirPair(self):
        act = self.sender()
        _topDir, _startDirOrModule = act.toolTip().split("\n")
        configName = str(act.text())
        self.loadSavedDirPair.emit(_startDirOrModule, _topDir, configName)
