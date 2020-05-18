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
from utest.core import appsettings
from utest.core import constants
from utest.core import testmanager
from utest.core import appsettings
from utest.ui import logbrowser
from utest.ui import rootpathedit
from utest.ui import testtreeview
from utest.ui import statuslabel
from utest.ui import uiutils
from utest.ui import configwindow
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
    _clearLogOnRunIcon = None
    _clearLogIcon = None
    _stopAtErrorIcon = None
    _runAllIcon = None
    _runSelectedIcon = None
    _panelStateIconSet = None


    def __init__(self, startDirOrModule=None, topDir=None, parent=None):
        parent = parent or dcc.findParentWindow()
        QtWidgets.QWidget.__init__(self, parent)

        self._initIcons()
        self.setWindowIcon(self._utestIcon)
        self._testManager = testmanager.TestManager(self, startDirOrModule, topDir)

        self._mainLay = uiutils.makeMainLayout(self)
        self.setContentsMargins(0, 0, 0, 0)

        # Top layout ------------------------------
        self._dirLayout = uiutils.makeMinorHorizontalLayout()
        self._makeDirWidgets()
        self._mainLay.addLayout(self._dirLayout)

        self._splitter = QtWidgets.QSplitter(self)
        self._mainLay.addWidget(self._splitter, 1)

        # left layout -----------------------------------
        self._leftWidget, leftLay = self._createSplitterContent()
    
        self._topLayout = uiutils.makeMinorHorizontalLayout()
        self._makeTopWidgets()
        leftLay.addLayout(self._topLayout)

        self._view = testtreeview.TestTreeView(self)
        self._view.setTestManager(self._testManager)
        self._view.runAllTest.connect(self.onRunAll)
        self._view.runTests.connect(self.onRunTests)

        leftLay.addWidget(self._view)

        # right layout -----------------------------------
        self._rightWidget, rightLay = self._createSplitterContent()
        self._logTopLayout = uiutils.makeMinorHorizontalLayout()
        self._logWgt = logbrowser.LogBrowser(self)
        self._makeLogTopLayout()
        rightLay.addLayout(self._logTopLayout, 0)
        rightLay.addWidget(self._logWgt, 1)

        # bottom layout -----------------------------------
        self._btmLayout = uiutils.makeMinorHorizontalLayout()
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

        self._restorePanelVisState()

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
        return wgt, splitterLay

    def _makeLogTopLayout(self):
        _console = QtWidgets.QLabel("Console")
        self._clearLogOnRunBtn = uiutils.makeIconButton(self._clearLogOnRunIcon, self)
        self._clearLogOnRunBtn.setCheckable(True)
        autoClear = bool(appsettings.get().simpleConfigValue(constants.CONFIG_KEY_AUTO_CLEAR_LOG_STATE))
        self._clearLogOnRunBtn.setChecked(autoClear)
        self._clearLogOnRunBtn.toggled.connect(self._onAutoClearButtonToggled)

        self._clearLogBtn = uiutils.makeIconButton(self._clearLogIcon, self)
        self._clearLogBtn.clicked.connect(self._logWgt.clear)

        self._logTopLayout.addWidget(_console, 0)
        self._logTopLayout.addStretch(1)
        self._logTopLayout.addWidget(self._clearLogOnRunBtn, 0)
        self._logTopLayout.addWidget(self._clearLogBtn, 0)

    @classmethod
    def _initSingleIcon(cls, iconVarName, iconFileName):
        iconPath = iconutils.iconPath(iconFileName)
        setattr(cls, iconVarName, QtGui.QIcon(iconPath))

    @classmethod
    def _initIcons(cls):
        if cls._panelStateIconSet:
            return

        panelStatePaths = iconutils.iconPathSet('panelMode.svg', 
                                    constants.PANEL_VIS_STATE_ICON_SUFFIXES,
                                    includeInput=False)
        cls._panelStateIconSet = [QtGui.QIcon(p) for p in panelStatePaths]

        cls._initSingleIcon("_utestIcon", "utest.svg")
        cls._initSingleIcon("_reimportIcon", "reimport.svg")
        cls._initSingleIcon("_clearIcon", "clear.svg")
        cls._initSingleIcon("_moreIcon", "more.svg")
        cls._initSingleIcon("_filterIcon", "stateFilter.svg")
        cls._initSingleIcon("_autoFilterIcon", "autoFilter.svg")
        cls._initSingleIcon("_resetIcon", "reset.svg")
        cls._initSingleIcon("_clearLogIcon", "clearLog.svg")
        cls._initSingleIcon("_clearLogOnRunIcon", "clearLogOnRun.svg")
        cls._initSingleIcon("_stopAtErrorIcon", "stopAtError.svg")
        cls._initSingleIcon("_runAllIcon", "runAll.svg")
        cls._initSingleIcon("_runSelectedIcon", "runSelected.svg")

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
        config = appsettings.get().testDirSettings()
        for key, pair in config.items():
            act = self._moreMenu.addAction(key)
            act.triggered.connect(self.onSavedDirPairLoad)
            act.setToolTip("\n".join(pair))
        self._moreMenu.addSeparator()
        act = self._moreMenu.addAction("Config..")
        act.triggered.connect(self._onConfigWindow)

    def _onConfigWindow(self):
        configwindow.ConfigWindow.show(self)

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

        self._panelVisBtn = uiutils.makeIconButton(self._panelStateIconSet[-1], self)
        self._panelVisBtn.clicked.connect(self._onPanelVisButtonClicked)

        self._dirLayout.addWidget(lbl)
        self._dirLayout.addWidget(self._rootDirLE)
        self._dirLayout.addWidget(self._browseBtn)
        self._dirLayout.addWidget(self._panelVisBtn)

        self._updateDirUI()

    def _makeTopWidgets(self):
        reimportBtn = uiutils.makeIconButton(self._reimportIcon, self)
        reimportBtn.clicked.connect(self.onReimportAndRefresh)
        self._topLayout.addWidget(reimportBtn)

        self._searchLE = QtWidgets.QLineEdit()
        self._searchLE.setPlaceholderText("Input to filter")
        self._searchLE.textChanged.connect(self.onFilterTextChanged)
        self._topLayout.addWidget(self._searchLE)

        self._clearSearchBtn = uiutils.makeIconButton(self._clearIcon, self)
        self._clearSearchBtn.setEnabled(False)
        self._clearSearchBtn.clicked.connect(self.clearSearch)
        self._topLayout.addWidget(self._clearSearchBtn)

        self._filterBtn, self._filterMenu = self._makeMenuToolButton(self._filterIcon)
        for lbl in constants.KEYWORD_TEST_STATES:
            act = self._filterMenu.addAction(lbl)
            act.triggered.connect(self.onAddFilter)
        self._topLayout.addWidget(self._filterBtn)

        self._autoFilterBtn = uiutils.makeIconButton(self._autoFilterIcon, self)
        self._autoFilterBtn.setCheckable(True)
        autoFilter = bool(appsettings.get().simpleConfigValue(constants.CONFIG_KEY_AUTO_FILTERING_STATE))
        self._autoFilterBtn.setChecked(autoFilter)
        self._autoFilterBtn.toggled.connect(self._onAutoFilterButtonToggled)
        self._topLayout.addWidget(self._autoFilterBtn)

    def _onAutoFilterButtonToggled(self, state):
        appsettings.get().saveSimpleConfig(constants.CONFIG_KEY_AUTO_FILTERING_STATE, state)

    def _onAutoClearButtonToggled(self, state):
        appsettings.get().saveSimpleConfig(constants.CONFIG_KEY_AUTO_CLEAR_LOG_STATE, state)
    
    def _onStopOnErrorButtonToggled(self, stop):
        self._testManager.setStopOnError(stop)
        appsettings.get().saveSimpleConfig(constants.CONFIG_KEY_STOP_ON_ERROR, stop)

    def _makeBtmButtons(self):
        self._stopAtErrorBtn = uiutils.makeIconButton(self._stopAtErrorIcon, self)
        self._stopAtErrorBtn.toggled.connect(self._onStopOnErrorButtonToggled)
        self._stopAtErrorBtn.setCheckable(True)
        stopOnError = bool(appsettings.get().simpleConfigValue(constants.CONFIG_KEY_STOP_ON_ERROR))
        self._stopAtErrorBtn.setChecked(stopOnError)
        self._testManager.setStopOnError(stopOnError)
        self._btmLayout.addWidget(self._stopAtErrorBtn, 0)

        self._resetAllBtn = uiutils.makeIconButton(self._resetIcon, self)
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

        settings = appsettings.get()
        settings.saveSimpleConfig(constants.CONFIG_KEY_LAST_SAVED_TEST_DIR, configName)

        self._updateWindowTitle(configName)
        self._updateDirUI()
        self._searchLE.clear()
        self.reload()

    def onRootPathEdited(self, startDir, topDir):
        self._testManager.setDirs(startDir, topDir)
        self._updateWindowTitle(startDir)
        self._updateDirUI()
        self._searchLE.clear()
        self.reload(keepUiStates=False)

    def _setPanelVisState(self, state, saveSettings=True):
        state = min(constants.PANEL_VIS_STATE_BOTH_ON, max(0, state))
        self._panelVisBtn.setIcon(self._panelStateIconSet[state])
        self._leftWidget.setVisible(state != constants.PANEL_VIS_STATE_RIGHT_ON)
        self._rightWidget.setVisible(state != constants.PANEL_VIS_STATE_LEFT_ON)
        if saveSettings:
            appsettings.get().saveSimpleConfig(constants.CONFIG_KEY_PANEL_VIS_STATE, state)
        
    def _restorePanelVisState(self):
        state = appsettings.get().simpleConfigValue(constants.CONFIG_KEY_PANEL_VIS_STATE,
            constants.PANEL_VIS_STATE_BOTH_ON
        )
        self._setPanelVisState(state, saveSettings=False)

    def _onPanelVisButtonClicked(self):
        leftVis = self._leftWidget.isVisible()
        rightVis = self._rightWidget.isVisible()
        state = constants.PANEL_VIS_STATE_BOTH_ON
        if not leftVis:
            state = constants.PANEL_VIS_STATE_RIGHT_ON
        elif not rightVis:
            state = constants.PANEL_VIS_STATE_LEFT_ON
        state = (state + 1) % 3
        self._setPanelVisState(state)

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
        settings = appsettings.get()
        name = settings.simpleConfigValue(constants.CONFIG_KEY_LAST_SAVED_TEST_DIR)
        if not name:
            return
            
        config = appsettings.get().testDirSettings()
        if name not in config or not config[name]:
            logger.error("The last setting name %s does not exist.", name)
            return

        _topDir, _startDirOrModule = config[name]
        self._testManager.setDirs(_startDirOrModule, _topDir)
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
        with appsettings.SettingsGroupContext(constants.CONFIG_KEY_SAVED_TEST_DIR):
            with appsettings.SettingsGroupContext(name[0]) as settings:
                settings.saveSimpleConfig(constants.CONFIG_KEY_TEST_TOP_DER, topDir, sync=False)
                settings.saveSimpleConfig(constants.CONFIG_KEY_TEST_START_DER, startDir, sync=False)

        settings.saveSimpleConfig(constants.CONFIG_KEY_LAST_SAVED_TEST_DIR, name[0])

        self._deferredRegenerateMenu()
        self._updateWindowTitle(name[0])

    def _deferredRegenerateMenu(self):
        QtCore.QTimer.singleShot(0, self._regenerateMenu)

    def _onDeleteCurrentDirSettings(self):
        config = appsettings.get().testDirSettings()
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

        with appsettings.SettingsGroupContext(constants.CONFIG_KEY_SAVED_TEST_DIR) as settings:
            for n in removeNames:
                settings.removeConfig(n)
                logger.info("Remove the dir setting: %s", n)

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
        if self._clearLogOnRunBtn.isChecked():
            self._logWgt.clear()
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
