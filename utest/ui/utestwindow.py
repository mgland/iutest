import logging
import os
import sys
import collections
import weakref

from utest import dcc
from utest.core import reimportall
from utest.qt import QtCore, QtGui, QtWidgets
from utest.core import pathutils
from utest.core import iconutils
from utest.core import settings
from utest.core import constants
from utest.core import testmanager
from utest.ui import logbrowser
from utest.ui import rootpathedit
from utest.ui import testtreeview
from utest.ui import statuslabel
from utest.libs import nose2
from utest.plugins import testlister
from utest.plugins import viewupdater

logger = logging.getLogger(__name__)


class UTestWindow(QtWidgets.QWidget):
    _utestIcon = None
    _reimportIcon = None
    _clearIcon = None
    _moreIcon = None
    _filterIcon = None
    _autoFilterIcon = None
    _resetIcon = None
    _clearLogIcon = None
    _stopAtErrorIcon = None
    _runAllIcon = None
    _runSelectedIcon = None

    _Settings = None
    _config_key_savedDir = "testDirs"
    _config_key_lastSavedDir = "lastTestDirs"
    _config_key_topDir = "topDir"
    _config_key_testRootDir = "testRootDir"

    def __init__(self, startDirOrModule=None, topDir=None, parent=None):
        parent = parent or dcc.findParentWindow()
        QtWidgets.QWidget.__init__(self, parent)

        self._initIcons()
        self.setWindowIcon(self._utestIcon)
        self._testManager = testmanager.TestManager(self, startDirOrModule, topDir)

        self._mainLay = QtWidgets.QVBoxLayout(self)
        self._mainLay.setContentsMargins(6, 6, 6, 6)
        self._mainLay.setSpacing(3)
        self.setContentsMargins(0, 0, 0, 0)

        # Top layout ------------------------------
        self._dirLayout = QtWidgets.QHBoxLayout()
        self._dirLayout.setSpacing(3)
        self._dirLayout.setContentsMargins(0, 0, 0, 0)
        self._makeDirWidgets()
        self._mainLay.addLayout(self._dirLayout)

        self._splitter = QtWidgets.QSplitter(self)
        self._mainLay.addWidget(self._splitter, 1)

        # left layout -----------------------------------
        leftLay = self._createSplitterContent()

        self._topLayout = QtWidgets.QHBoxLayout()
        self._topLayout.setSpacing(3)
        self._topLayout.setContentsMargins(0, 0, 0, 0)
        self._makeTopWidgets()
        leftLay.addLayout(self._topLayout)

        self._view = testtreeview.TestTreeView(self)
        self._view.setTestManager(self._testManager)
        self._view.runAllTest.connect(self.onRunAll)
        self._view.runTests.connect(self.onRunTests)

        leftLay.addWidget(self._view)

        # right layout -----------------------------------
        rightLay = self._createSplitterContent()
        self._logWgt = logbrowser.LogBrowser(self)
        rightLay.addWidget(self._logWgt)

        # bottom layout -----------------------------------
        self._btmLayout = QtWidgets.QHBoxLayout()
        self._btmLayout.setSpacing(3)
        self._btmLayout.setContentsMargins(0, 3, 0, 0)
        self._makeBtmButtons()
        self._mainLay.addLayout(self._btmLayout)

        # bottom -----------------------------------
        self._statusLbl = statuslabel.StatusLabel(self)
        self._mainLay.addWidget(self._statusLbl)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(constants.APP_NAME)

        self.resize(QtCore.QSize(850, 500))
        self._splitter.setSizes([350, 500])

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)  # for reimport convenience.

        self._loadLastDirsFromSettings()
        self._testManager.setBeforeTestStartHook(self._beforeRunningTests)
        self.reload(keepUiStates=False)

    def setIsStandalone(self, isStandalone):
        if isStandalone:
            pal = self.palette()

            pal.setColor(pal.Window, QtGui.QColor(68,68,68))
            pal.setColor(pal.Background, QtGui.QColor(68,68,68))
            pal.setColor(pal.WindowText, QtGui.QColor(200,200,200))
            pal.setColor(pal.Foreground, QtGui.QColor(200,200,200))
            pal.setColor(pal.Base, QtGui.QColor(46,46,46))
            pal.setColor(pal.AlternateBase, QtGui.QColor(43,43,43))
            pal.setColor(pal.ToolTipBase, QtGui.QColor(46,46,46))
            pal.setColor(pal.ToolTipText, QtGui.QColor(200,200,200))
            pal.setColor(pal.Text, QtGui.QColor(200,200,200))
            pal.setColor(pal.Button, QtGui.QColor(93,93,93))
            pal.setColor(pal.ButtonText, QtGui.QColor(238,238,238))
            pal.setColor(pal.BrightText, QtGui.QColor(238,238,238))
            
            pal.setColor(pal.Light, QtGui.QColor(93,93,93))
            pal.setColor(pal.Midlight, QtGui.QColor(50,50,50))
            pal.setColor(pal.Dark, QtGui.QColor(43,43,43))
            pal.setColor(pal.Mid, QtGui.QColor(46,46,46))
            pal.setColor(pal.Shadow, QtGui.QColor(43,43,43))

            pal.setColor(pal.Highlight, QtGui.QColor(82,133,166))
            pal.setColor(pal.HighlightedText, QtGui.QColor(238,238,238))
            self.setPalette(pal)
            
    def _createSplitterContent(self):
        wgt = QtWidgets.QWidget(self)
        splitterLay = QtWidgets.QVBoxLayout(wgt)
        splitterLay.setSpacing(3)
        splitterLay.setContentsMargins(0, 0, 0, 0)
        self._splitter.addWidget(wgt)
        return splitterLay

    @classmethod
    def _getSettings(cls):
        if cls._Settings:
            return cls._Settings

        cls._Settings = settings.createIniSettings("TestManager")
        return cls._Settings

    @classmethod
    def _initSingleIcon(cls, iconVarName, iconFileName):
        iconPath = iconutils.iconPath(iconFileName)
        setattr(cls, iconVarName, QtGui.QIcon(iconPath))

    @classmethod
    def _initIcons(cls):
        if cls._utestIcon:
            return

        cls._initSingleIcon("_utestIcon", "utest.svg")
        cls._initSingleIcon("_reimportIcon", "reimport.svg")
        cls._initSingleIcon("_clearIcon", "clear.svg")
        cls._initSingleIcon("_moreIcon", "more.svg")
        cls._initSingleIcon("_filterIcon", "stateFilter.svg")
        cls._initSingleIcon("_autoFilterIcon", "autoFilter.svg")
        cls._initSingleIcon("_resetIcon", "reset.svg")
        cls._initSingleIcon("_clearLogIcon", "clearLog.svg")
        cls._initSingleIcon("_stopAtErrorIcon", "stopAtError.svg")
        cls._initSingleIcon("_runAllIcon", "runAll.svg")
        cls._initSingleIcon("_runSelectedIcon", "runSelected.svg")

    def _makeIconButton(self, icon):
        btn = QtWidgets.QPushButton("", self)
        btn.setIcon(icon)
        btn.setFlat(True)
        btn.setIconSize(QtCore.QSize(20, 20))
        btn.setFixedSize(QtCore.QSize(24, 24))
        return btn

    def _onStopOnErrorStageChanged(self, stop):
        self._testManager.setStopOnError(stop)

    def _regenerateMenu(self):
        self._moreMenu.clear()

        act = self._moreMenu.addAction("Browse Test Root Dir ...")
        act.triggered.connect(self._onBrowseTestsRootDir)
        act = self._moreMenu.addAction("Browse Top Root Dir ...")
        act.triggered.connect(self._onBrowseTopDir)
        self._moreMenu.addSeparator()
        act = self._moreMenu.addAction("Save Current Path Settings ...")
        act.triggered.connect(self._onSaveCurrentDirSettings)
        act = self._moreMenu.addAction("Delete Current Settings ...")
        act.triggered.connect(self._onDeleteCurrentDirSettings)
        self._moreMenu.addSeparator()

        # Read settings:
        config = self._readDirSettings()
        for key, pair in config.items():
            act = self._moreMenu.addAction(key)
            act.triggered.connect(self.onSavedDirPairLoad)
            act.setToolTip("\n".join(pair))

    def _makeMenuToolButton(self, icon):
        btn = QtWidgets.QToolButton(self)
        btn.setIcon(icon)
        btn.setPopupMode(btn.InstantPopup)
        menu = QtWidgets.QMenu(btn)
        btn.setMenu(menu)
        return (btn, menu)

    def _makeDirWidgets(self):
        lbl = QtWidgets.QLabel("Test Root")
        self._rootDirLE = rootpathedit.RootPathEdit(self)
        self._rootDirLE.rootPathChanged.connect(self.onRootPathEdited)

        self._browseBtn, self._moreMenu = self._makeMenuToolButton(self._moreIcon)
        self._regenerateMenu()

        self._dirLayout.addWidget(lbl)
        self._dirLayout.addWidget(self._rootDirLE)
        self._dirLayout.addWidget(self._browseBtn)

        self._updateDirUI()

    def _makeTopWidgets(self):
        reimportBtn = self._makeIconButton(self._reimportIcon)
        reimportBtn.clicked.connect(self.onReimportAndRefresh)
        self._topLayout.addWidget(reimportBtn)

        self._searchLE = QtWidgets.QLineEdit()
        self._searchLE.setPlaceholderText("Input to filter")
        self._searchLE.textChanged.connect(self.onFilterTextChanged)
        self._topLayout.addWidget(self._searchLE)

        self._clearSearchBtn = self._makeIconButton(self._clearIcon)
        self._clearSearchBtn.setEnabled(False)
        self._clearSearchBtn.clicked.connect(self.clearSearch)
        self._topLayout.addWidget(self._clearSearchBtn)

        self._filterBtn, self._filterMenu = self._makeMenuToolButton(self._filterIcon)
        for lbl in constants.KEYWORD_TEST_STATES:
            act = self._filterMenu.addAction(lbl)
            act.triggered.connect(self.onAddFilter)
        self._topLayout.addWidget(self._filterBtn)

        self._autoFilterBtn = self._makeIconButton(self._autoFilterIcon)
        self._autoFilterBtn.setCheckable(True)
        self._topLayout.addWidget(self._autoFilterBtn)

    def _makeBtmButtons(self):
        self._clearLogBtn = self._makeIconButton(self._clearLogIcon)
        self._clearLogBtn.clicked.connect(self._logWgt.clear)
        self._btmLayout.addWidget(self._clearLogBtn, 0)

        self._stopAtErrorBtn = self._makeIconButton(self._stopAtErrorIcon)
        self._stopAtErrorBtn.toggled.connect(self._onStopOnErrorStageChanged)
        self._stopAtErrorBtn.setCheckable(True)
        self._btmLayout.addWidget(self._stopAtErrorBtn, 0)

        self._resetAllBtn = self._makeIconButton(self._resetIcon)
        self._resetAllBtn.clicked.connect(self._view.resetAllItemsToNormal)
        self._btmLayout.addWidget(self._resetAllBtn, 1)

        self._executeSelectedBtn = QtWidgets.QPushButton("Run Selected Tests", self)
        self._executeSelectedBtn.clicked.connect(self.onRunSelected)
        self._executeSelectedBtn.setIcon(self._runSelectedIcon)
        self._btmLayout.addWidget(self._executeSelectedBtn, 1)

        self._executeAllBtn = QtWidgets.QPushButton("Run All Tests", self)
        self._executeAllBtn.setIcon(self._runAllIcon)
        self._executeAllBtn.clicked.connect(self.onRunAll)
        self._btmLayout.addWidget(self._executeAllBtn, 1)

    def onReimportAndRefresh(self):
        if reimportall.reimportAllChangedPythonModules():
            self.reload(keepUiStates=True)
            self._applyCurrentFilter()

    def onAddFilter(self):
        stateKeyword = self.sender().text()
        search = self._searchLE.text().strip()
        if not search:
            self._searchLE.setText(stateKeyword)
            return
        parts = search.split(" ")
        if stateKeyword in parts:
            return
        parts.insert(0, stateKeyword)
        self._searchLE.setText(" ".join(parts))

    def onSavedDirPairLoad(self):
        act = self.sender()
        _topDir, _startDirOrModule = act.toolTip().split("\n")
        self._testManager.setTopDir(_topDir)
        self._testManager.setStartDirOrModule(_startDirOrModule)

        configName = act.text()

        settings = self._getSettings()
        settings.setValue(self._config_key_lastSavedDir, configName)
        settings.sync()

        self._updateWindowTitle(configName)
        self._updateDirUI()
        self._searchLE.clear()
        self.reload()

    def onRootPathEdited(self, startDir, topDir):
        self._testManager.setDirs(startDir, topDir)
        self._updateWindowTitle(startDir)
        self._updateDirUI()
        self._searchLE.clear()
        self.reload()

    def _updateDirUI(self):
        self._rootDirLE.setText(self._testManager.startDirOrModule())
        self._rootDirLE.setToolTip(self._testManager.topDir())

    def _onBrowseTestsRootDir(self):
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Pick the Test Root Directory"
        )
        if dirPath:
            self._testManager.setStartDirOrModule(dirPath)
            self._updateDirUI()
            self._searchLE.clear()
            self.reload()

    def _onBrowseTopDir(self):
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Pick the Top Python Directory"
        )
        if dirPath:
            self._testManager.setTopDir(dirPath)

        self._searchLE.clear()
        self._updateDirUI()
        self.reload()

    def _updateWindowTitle(self, configName):
        self.setWindowTitle("{} - {}".format(constants.APP_NAME, configName))

    def _loadLastDirsFromSettings(self):
        settings = self._getSettings()
        name = settings.value(self._config_key_lastSavedDir)
        if not name:
            return
        config = self._readDirSettings()
        if name not in config or not config[name]:
            logger.error("The last setting name %s does not exist.", name)
            return

        _topDir, _startDirOrModule = config[name]
        self._testManager.setDirs(_topDir, _startDirOrModule)
        self._updateDirUI()
        self._updateWindowTitle(name)

    def _onSaveCurrentDirSettings(self):
        startDir = self._testManager.startDirOrModule()
        name = QtWidgets.QInputDialog.getText(
            self, "Save Dir Settings", "Input a name for the test set:", text=startDir
        )

        if not name[-1] or not name[0]:
            return

        topDir = self._testManager.topDir()
        settings = self._getSettings()

        settings.beginGroup(self._config_key_savedDir)
        settings.setValue("%s/%s" % (name[0], self._config_key_topDir), topDir)
        settings.setValue("%s/%s" % (name[0], self._config_key_testRootDir), startDir)
        settings.endGroup()

        settings.setValue(self._config_key_lastSavedDir, name[0])

        settings.sync()
        self._deferredRegenerateMenu()
        self._updateWindowTitle(name[0])

    def _deferredRegenerateMenu(self):
        QtCore.QTimer.singleShot(0, self._regenerateMenu)

    def _readDirSettings(self):
        settings = self._getSettings()
        logger.debug("Settings ini file:%s", settings.fileName())
        settings.beginGroup(self._config_key_savedDir)
        names = settings.childGroups()
        data = collections.OrderedDict()
        for n in names:
            settings.beginGroup(n)
            data[n] = (
                settings.value(self._config_key_topDir),
                settings.value(self._config_key_testRootDir),
            )
            settings.endGroup()

        settings.endGroup()
        return data

    def _onDeleteCurrentDirSettings(self):
        config = self._readDirSettings()
        removeNames = []
        startDir = self._testManager.startDirOrModule()
        for name, pair in config.items():
            _, root = pair
            if root == startDir:
                removeNames.append(name)
        if not removeNames:
            logger.warning("Current dir settings was not saved before.")
            return

        msg = "Are you sure to delete these dir settings: %s" % removeNames
        answer = QtWidgets.QMessageBox.question(self, "Remove Current Dir Setting", msg)
        if answer != QtWidgets.QMessageBox.Yes:
            return

        settings = self._getSettings()
        settings.beginGroup(self._config_key_savedDir)
        for n in removeNames:
            settings.remove(n)
            logger.info("Remove the dir setting: %s", n)
        settings.endGroup()
        self._deferredRegenerateMenu()

    def onRunAll(self):
        self._view.resetAllItemsToNormal()
        self._searchLE.clear()
        self._testManager.runAllTests()

    def onRunTests(self, testIds):
        self._testManager.runTests(*testIds)

    def onRunSelected(self):
        self._view.runSelectedTests()

    def clearSearch(self):
        self._searchLE.clear()

    def reload(self, keepUiStates=True):
        self._view.reload(keepUiStates=keepUiStates)
        if not self._testManager.startDirOrModule():
            self.updateButtonsEnabled()
            return

        self.updateButtonsEnabled()
        self._statusLbl.reportTestCount(self._view.testCount())
        self._statusLbl.reportTestCount(self._view.testCount())

    def _applyCurrentFilter(self):
        self.onFilterTextChanged(self._searchLE.text())

    def updateButtonsEnabled(self):
        enabled = self._view.hasTests()
        self._resetAllBtn.setEnabled(enabled)
        self._executeAllBtn.setEnabled(enabled)
        self._executeSelectedBtn.setEnabled(enabled)

    def _beforeRunningTests(self, tests):
        self.onTestRunningSessionStart()
        self._logWgt.onTestStart()
        self._view.resetTestItemsById(tests)

    def onFilterTextChanged(self, txt):
        lowerTxt = txt.strip().lower()
        keywords = lowerTxt.split(" ")
        self._clearSearchBtn.setEnabled(bool(keywords))
        self._view.setFilterKeywords(keywords)

    def onSingleTestStartToRun(self, testId, startTime):
        self._view.onSingleTestStartToRun(testId, startTime)

    def onSingleTestStop(self, testId, endTime):
        self._view.onSingleTestStop(testId, endTime)
        self._statusLbl.updateReport()

    def showResultOnItemByTestId(self, testId, state):
        self._view.showResultOnItemByTestId(testId, state)

    def onTestRunningSessionStart(self):
        self._statusLbl.setText("Running tests...")
        self._logWgt.logSeparator()

    def onAllTestsFinished(self):
        self._view.onAllTestsFinished()
        if self._autoFilterBtn.isChecked():
            self._searchLE.setText(constants.KEYWORD_TEST_STATE_RUN)
        self._statusLbl.updateReport()

    def repaintUi(self):
        eventFlags = (
            QtCore.QEventLoop.ExcludeSocketNotifiers
            | QtCore.QEventLoop.ExcludeUserInputEvents
        )
        QtWidgets.QApplication.processEvents(eventFlags)


if __name__ == "__main__":
    manager = UTestWindow()
    manager.show()
