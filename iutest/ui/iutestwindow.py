import logging
import os
import sys
import collections
import weakref

from iutest import dcc
from iutest.core import importutils
from iutest.qt import QtCore, QtGui, QtWidgets, iconFromPath
from iutest.core import pathutils
from iutest.core import iconutils
from iutest.core import appsettings
from iutest.core import constants
from iutest.core import testmanager
from iutest.core import uistream
from iutest.ui import logbrowser
from iutest.ui import rootpathedit
from iutest.ui import testtreeview
from iutest.ui import statuslabel
from iutest.ui import uiutils
from iutest.ui import configwindow

logger = logging.getLogger(__name__)


class IUTestWindow(QtWidgets.QWidget):
    _iutestIcon = None
    _reimportIcon = None
    _reloadUiIcon = None
    _clearIcon = None
    _moreIcon = None
    _filterIcon = None
    _autoFilterIcon = None
    _resetIcon = None
    _clearLogOnRunIcon = None
    _clearLogIcon = None
    _stopAtErrorIcon = None
    _reimportAndRunIcon = None
    _runPartialIcon = None
    _runAllIcon = None
    _runSelectedIcon = None
    _panelStateIconSet = None

    def __init__(self, startDirOrModule=None, topDir=None, parent=None):
        parent = parent or dcc.findParentWindow()
        QtWidgets.QWidget.__init__(self, parent)

        self._initIcons()

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

        _topLayout = uiutils.makeMinorHorizontalLayout()
        self._makeTopWidgets(_topLayout)
        leftLay.addLayout(_topLayout)

        self._view = testtreeview.TestTreeView(self)
        self._view.runAllTest.connect(self._runAllTests)
        self._view.runTests.connect(self._runTests)
        self._view.runSetupOnly.connect(self._runTestSetupOnly)
        self._view.runWithoutTearDown.connect(self._runTestWithoutTearDown)
        self._view.itemSelectionChanged.connect(self._viewSelectionChanged)

        leftLay.addWidget(self._view)

        # right layout -----------------------------------
        self._rightWidget, rightLay = self._createSplitterContent()
        _logTopLayout = uiutils.makeMinorHorizontalLayout()
        self._logWgt = logbrowser.LogBrowser(self)
        self._makeLogTopLayout(_logTopLayout)
        rightLay.addLayout(_logTopLayout, 0)
        rightLay.addWidget(self._logWgt, 1)

        self._splitter.setSizes([230, 500])
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)

        # bottom -----------------------------------
        _btmLayout = uiutils.makeMinorHorizontalLayout()
        self._makeRunButtons(_btmLayout)
        self._mainLay.addLayout(_btmLayout)

        self._statusLbl = statuslabel.StatusLabel(self)
        self._mainLay.addWidget(self._statusLbl)

        self.resize(QtCore.QSize(900, 500))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)  # for reimport convenience.
        self.setTabOrder(self._rootDirLE, self._searchLE)
        self.setTabOrder(self._searchLE, self._view)
        self.setTabOrder(self._view, self._logWgt)
        self.setWindowIcon(self._iutestIcon)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(constants.APP_NAME)

        self._loadLastDirsFromSettings()
        self._restorePanelVisState()

        self.resetUiTestManager()

        QtCore.QTimer.singleShot(0, self._initialLoad)

    def resetUiTestManager(self):
        self._view.setTestManager(self._testManager)
        self._statusLbl.setTestManager(self._testManager)

    def _initialLoad(self):
        self.reload(keepUiStates=False)
        self._updateReimportRerunButtonEnabled()

    def _createSplitterContent(self):
        wgt = QtWidgets.QWidget(self)
        splitterLay = QtWidgets.QVBoxLayout(wgt)
        splitterLay.setSpacing(3)
        splitterLay.setContentsMargins(0, 0, 0, 0)
        self._splitter.addWidget(wgt)
        return wgt, splitterLay

    def _makeLogTopLayout(self, layout):
        _console = QtWidgets.QLabel("Console")
        self._clearLogOnRunBtn = uiutils.makeIconButton(self._clearLogOnRunIcon, self)
        self._clearLogOnRunBtn.setToolTip(
            "Clear the log browser automatically before every test run."
        )
        self._clearLogOnRunBtn.setCheckable(True)
        autoClear = appsettings.get().simpleConfigBoolValue(
            constants.CONFIG_KEY_AUTO_CLEAR_LOG_STATE
        )
        self._clearLogOnRunBtn.setChecked(autoClear)
        self._clearLogOnRunBtn.toggled.connect(self._onAutoClearButtonToggled)

        self._clearLogBtn = uiutils.makeIconButton(self._clearLogIcon, self)
        self._clearLogBtn.setToolTip("Clear the log browser logging.")
        self._clearLogBtn.clicked.connect(self._logWgt.clear)

        layout.addWidget(_console, 0)
        layout.addStretch(1)
        layout.addWidget(self._clearLogOnRunBtn, 0)
        layout.addWidget(self._clearLogBtn, 0)

    @classmethod
    def _initSingleIcon(cls, iconVarName, iconFileName):
        iconPath = iconutils.iconPath(iconFileName)
        setattr(cls, iconVarName, iconFromPath(iconPath))

    @classmethod
    def _initIcons(cls):
        if cls._panelStateIconSet:
            return

        panelStatePaths = iconutils.iconPathSet(
            "panelMode.svg", constants.PANEL_VIS_STATE_ICON_SUFFIXES, includeInput=False
        )
        cls._panelStateIconSet = [iconFromPath(p) for p in panelStatePaths]

        cls._initSingleIcon("_iutestIcon", "iutest.svg")
        cls._initSingleIcon("_reimportIcon", "reimport.svg")
        cls._initSingleIcon("_reloadUiIcon", "reloadUI.svg")
        cls._initSingleIcon("_clearIcon", "clear.svg")
        cls._initSingleIcon("_moreIcon", "more.svg")
        cls._initSingleIcon("_filterIcon", "stateFilter.svg")
        cls._initSingleIcon("_autoFilterIcon", "autoFilter.svg")
        cls._initSingleIcon("_resetIcon", "reset.svg")
        cls._initSingleIcon("_clearLogIcon", "clearLog.svg")
        cls._initSingleIcon("_clearLogOnRunIcon", "clearLogOnRun.svg")
        cls._initSingleIcon("_stopAtErrorIcon", "stopAtError.svg")
        cls._initSingleIcon("_reimportAndRunIcon", "reimportAndRerun.svg")
        cls._initSingleIcon("_runPartialIcon", "run_partial.svg")
        cls._initSingleIcon("_runAllIcon", "runAll.svg")
        cls._initSingleIcon("_runSelectedIcon", "runSelected.svg")

    def _regenerateMoreFeatureMenu(self):
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
            act.triggered.connect(self._loadSavedDirPair)
            act.setToolTip("\n".join(pair))
        self._moreMenu.addSeparator()
        act = self._moreMenu.addAction("Config..")
        act.triggered.connect(self._showConfigWindow)

    def _showConfigWindow(self):
        configwindow.ConfigWindow.show(self)

    def _makeMenuToolButton(self, icon, toolTip):
        btn = QtWidgets.QToolButton(self)
        btn.setIcon(icon)
        btn.setToolTip(toolTip)
        btn.setPopupMode(btn.InstantPopup)
        menu = QtWidgets.QMenu(btn)
        btn.setMenu(menu)
        return (btn, menu)

    def _makeDirWidgets(self):
        lbl = QtWidgets.QLabel("Test Root")
        lbl.setToolTip(
            "Input a python module path or an absolute dir path in the lineEdit for the tests."
        )
        self._rootDirLE = rootpathedit.RootPathEdit(self)
        self._rootDirLE.rootPathChanged.connect(self._switchToTestRootPath)

        self._browseBtn, self._moreMenu = self._makeMenuToolButton(
            self._moreIcon, "Click to access more features."
        )
        self._regenerateMoreFeatureMenu()

        self._panelVisBtn = uiutils.makeIconButton(self._panelStateIconSet[-1], self)
        self._panelVisBtn.setToolTip(
            "Switch the test tree view and the log browser visibility."
        )
        self._panelVisBtn.clicked.connect(self._onPanelVisButtonClicked)

        self._dirLayout.addWidget(lbl)
        self._dirLayout.addWidget(self._rootDirLE)
        self._dirLayout.addWidget(self._browseBtn)
        self._dirLayout.addWidget(self._panelVisBtn)

        self._updateDirUI()

    def _makeTopWidgets(self, layout):
        reimportBtn = uiutils.makeIconButton(self._reimportIcon, self)
        reimportBtn.setToolTip("Reimport all changed python module.")
        reimportBtn.clicked.connect(self._reimportAllChangedModules)
        layout.addWidget(reimportBtn)

        reloadUIBtn = uiutils.makeIconButton(self._reloadUiIcon, self)
        reloadUIBtn.setToolTip("Recollect tests and reload the test tree view below.")
        reloadUIBtn.clicked.connect(self._onReloadUiButtonClicked)
        layout.addWidget(reloadUIBtn)

        self._searchLE = QtWidgets.QLineEdit()
        self._searchLE.setToolTip(
            "Input keywords to filter the tests, separated by space.\n"
            "For normal keyword, the match operation is 'AND'\n"
            "For state keyword starting with ':', the match operation is 'OR'."
        )
        self._searchLE.setPlaceholderText("Input to filter")
        self._searchLE.textChanged.connect(self._applyFilterText)
        layout.addWidget(self._searchLE)

        self._clearFilterBtn = uiutils.makeIconButton(self._clearIcon, self)
        self._clearFilterBtn.setToolTip("Clear all filters.")
        self._clearFilterBtn.setEnabled(False)
        self._clearFilterBtn.clicked.connect(self._clearFilter)
        layout.addWidget(self._clearFilterBtn)

        self._filterBtn, self._filterMenu = self._makeMenuToolButton(
            self._filterIcon, "Click to apply more predefined filters."
        )
        for lbl in constants.KEYWORD_TEST_STATES:
            act = self._filterMenu.addAction(lbl)
            act.triggered.connect(self._addStateFilter)
        layout.addWidget(self._filterBtn)

        self._autoFilterBtn = uiutils.makeIconButton(self._autoFilterIcon, self)
        self._autoFilterBtn.setToolTip(
            "Apply a ':ran' filter automatically after every test run so that only the run tests shown in the view."
        )
        self._autoFilterBtn.setCheckable(True)
        autoFilter = appsettings.get().simpleConfigBoolValue(
            constants.CONFIG_KEY_AUTO_FILTERING_STATE
        )
        self._autoFilterBtn.setChecked(autoFilter)
        self._autoFilterBtn.toggled.connect(self._onAutoFilterButtonToggled)
        layout.addWidget(self._autoFilterBtn)

    def _onAutoFilterButtonToggled(self, state):
        appsettings.get().saveSimpleConfig(
            constants.CONFIG_KEY_AUTO_FILTERING_STATE, state
        )

    def _onAutoClearButtonToggled(self, state):
        appsettings.get().saveSimpleConfig(
            constants.CONFIG_KEY_AUTO_CLEAR_LOG_STATE, state
        )

    def _onStopOnErrorButtonToggled(self, stop):
        self._testManager.setStopOnError(stop)
        appsettings.get().saveSimpleConfig(constants.CONFIG_KEY_STOP_ON_ERROR, stop)

    def _makeRunButtons(self, _btmLayout):
        self._stopAtErrorBtn = uiutils.makeIconButton(self._stopAtErrorIcon, self)
        self._stopAtErrorBtn.toggled.connect(self._onStopOnErrorButtonToggled)
        self._stopAtErrorBtn.setToolTip(
            "Stop the tests running once it encounters a test error/failure."
        )
        self._stopAtErrorBtn.setCheckable(True)
        stopOnError = appsettings.get().simpleConfigBoolValue(
            constants.CONFIG_KEY_STOP_ON_ERROR
        )
        self._stopAtErrorBtn.setChecked(stopOnError)
        self._testManager.setStopOnError(stopOnError)
        _btmLayout.addWidget(self._stopAtErrorBtn, 0)

        self._resetAllBtn = uiutils.makeIconButton(self._resetIcon, self)
        self._resetAllBtn.setToolTip(
            "Reset the test item states, icons and stats and collapse the tree view items in a certain level."
        )
        self._resetAllBtn.clicked.connect(self._view.resetAllItemsToNormal)
        _btmLayout.addWidget(self._resetAllBtn, 1)

        self._runSelectedBtn = QtWidgets.QPushButton("Run &Selected", self)
        self._runSelectedBtn.setToolTip("Run the selected tests in the view.")
        self._runSelectedBtn.clicked.connect(self._runViewSelectedTests)
        self._runSelectedBtn.setIcon(self._runSelectedIcon)
        _btmLayout.addWidget(self._runSelectedBtn, 1)

        self._runAllBtn = QtWidgets.QPushButton("Run &All", self)
        self._runAllBtn.setToolTip(
            "Run all the tests, including those filtered from the view."
        )
        self._runAllBtn.setIcon(self._runAllIcon)
        self._runAllBtn.clicked.connect(self._runAllTests)
        _btmLayout.addWidget(self._runAllBtn, 1)

        self._reimportAndRerunBtn = QtWidgets.QPushButton("&Reload && Rerun", self)
        self._reimportAndRerunBtn.setToolTip(
            "Reimport all changed python modules and rerun the last tests."
        )
        self._reimportAndRerunBtn.clicked.connect(self._reimportPyAndRerun)
        self._reimportAndRerunBtn.setIcon(self._reimportAndRunIcon)
        _btmLayout.addWidget(self._reimportAndRerunBtn, 1)

        _runMoreBtn = self._makeRunMoreButton()
        _btmLayout.addWidget(_runMoreBtn, 0)

    def _makeRunMoreButton(self):
        _runMoreBtn = QtWidgets.QToolButton(self)
        _runMoreBtn.setIcon(self._runPartialIcon)
        _runMoreBtn.setAutoRaise(True)
        _runMoreBtn.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        _runMoreBtn.setPopupMode(_runMoreBtn.InstantPopup)
        self._runSetupAct = QtWidgets.QAction("Run setUp( ) Only", self)
        self._runSetupAct.triggered.connect(self._runTestSetupOnly)
        self._runNoTearDown = QtWidgets.QAction("Run without tearDown( )", self)
        self._runNoTearDown.triggered.connect(self._runTestWithoutTearDown)

        menu = QtWidgets.QMenu(_runMoreBtn)
        menu.addAction(self._runSetupAct)
        menu.addAction(self._runNoTearDown)
        _runMoreBtn.setMenu(menu)
        return _runMoreBtn

    def _reimportAllChangedModules(self):
        importutils.reimportAllChangedPythonModules()

    def _onReloadUiButtonClicked(self):
        self.reload(keepUiStates=True)
        self._applyCurrentFilter(removeStateFilters=True, keepUiStates=True)

    def _addStateFilter(self):
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

    def _saveLastTestDir(self, startDir, topDir):
        settings = appsettings.get()
        settings.saveSimpleConfig(
            constants.CONFIG_KEY_LAST_TEST_ROOT_DIR, startDir, sync=False
        )
        settings.saveSimpleConfig(constants.CONFIG_KEY_LAST_TOP_DIR, topDir, sync=True)
        logger.info("Save the last test root: %s", startDir)

    def _loadSavedDirPair(self):
        act = self.sender()
        _topDir, _startDirOrModule = act.toolTip().split("\n")
        self._testManager.setTopDir(_topDir)
        self._testManager.setStartDirOrModule(_startDirOrModule)

        configName = act.text()
        self._saveLastTestDir(_startDirOrModule, _topDir)
        self._updateWindowTitle(configName)
        self._updateDirUI()
        self._searchLE.clear()
        self.reload()

    def _switchToTestRootPath(self, startDir, topDir):
        self._testManager.setDirs(startDir, topDir)
        self._updateWindowTitle(startDir)
        self._updateDirUI()
        self._searchLE.clear()
        self.reload(keepUiStates=False)
        if not self._testManager.lastListerError():
            self._saveLastTestDir(startDir, topDir)

    def _setPanelVisState(self, state, saveSettings=True):
        state = min(constants.PANEL_VIS_STATE_BOTH_ON, max(0, int(state)))
        self._panelVisBtn.setIcon(self._panelStateIconSet[state])
        self._leftWidget.setVisible(state != constants.PANEL_VIS_STATE_RIGHT_ON)
        self._rightWidget.setVisible(state != constants.PANEL_VIS_STATE_LEFT_ON)
        if saveSettings:
            appsettings.get().saveSimpleConfig(
                constants.CONFIG_KEY_PANEL_VIS_STATE, state
            )

    def _restorePanelVisState(self):
        state = appsettings.get().simpleConfigIntValue(
            constants.CONFIG_KEY_PANEL_VIS_STATE, constants.PANEL_VIS_STATE_BOTH_ON
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

    def _configNameFromStartAndTopDir(self, startDir, topDir):
        config = appsettings.get().testDirSettings()
        for name in config:
            _topDir, _startDirOrModule = config[name]
            if _topDir == topDir and _startDirOrModule == startDir:
                return name
        return startDir

    def _loadLastDirsFromSettings(self):
        settings = appsettings.get()
        startDirOrModule = settings.simpleConfigStrValue(
            constants.CONFIG_KEY_LAST_TEST_ROOT_DIR
        )
        if not startDirOrModule:
            return

        topDir = settings.simpleConfigStrValue(constants.CONFIG_KEY_LAST_TOP_DIR)

        self._testManager.setDirs(startDirOrModule, topDir)
        self._updateDirUI()
        self._updateWindowTitle(
            self._configNameFromStartAndTopDir(startDirOrModule, topDir)
        )

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
                settings.saveSimpleConfig(
                    constants.CONFIG_KEY_TEST_TOP_DER, topDir, sync=False
                )
                settings.saveSimpleConfig(
                    constants.CONFIG_KEY_TEST_START_DER, startDir, sync=False
                )

        self._saveLastTestDir(startDir, topDir)
        self._deferredRegenerateMenu()
        self._updateWindowTitle(name[0])

    def _deferredRegenerateMenu(self):
        QtCore.QTimer.singleShot(0, self._regenerateMoreFeatureMenu)

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

        with appsettings.SettingsGroupContext(
            constants.CONFIG_KEY_SAVED_TEST_DIR
        ) as settings:
            for n in removeNames:
                settings.removeConfig(n)
                logger.info("Remove the dir setting: %s", n)

        self._deferredRegenerateMenu()

    def _runAllTests(self):
        self._view.resetAllItemsToNormal()
        self._searchLE.clear()
        self._testManager.runAllTests()
        self._updateReimportRerunButtonEnabled()

    def _runTests(self, testIds):
        if not testIds:
            return

        self._beforeRunningTests(testIds)
        self._testManager.runTests(*testIds)
        self._updateReimportRerunButtonEnabled()

    def _viewSelectionChanged(self):
        hasSel = self._view.hasSelectedTests()
        self._runSelectedBtn.setEnabled(hasSel)
        hasSelForPartialRun = self._view.hasSelectedTests(hasSelectedTestOrCase=True)
        self._runSetupAct.setEnabled(hasSelForPartialRun)
        self._runNoTearDown.setEnabled(hasSelForPartialRun)

    def _runViewSelectedTests(self):
        self._runTests(self._view.selectedTestIds())

    def _updateReimportRerunButtonEnabled(self):
        self._reimportAndRerunBtn.setEnabled(
            bool(self._testManager.lastRunTestIds())
        )

    def _reimportPyAndRerun(self):
        importutils.reimportAllChangedPythonModules()
        lastRunIds = self._testManager.lastRunTestIds()
        if not lastRunIds:
            logger.warning("Didn't find the last run tests.")
            return

        self._runTests(lastRunIds)

    def _runTestSetupOnly(self):
        self._runPartialTest(constants.RUN_TEST_SETUP_ONLY)

    def _runTestWithoutTearDown(self):
        self._runPartialTest(constants.RUN_TEST_NO_TEAR_DOWN)

    def _runPartialTest(self, partialMode):
        testId = self._view.firstSelectedTestOrTestCase()
        if not testId:
            logger.error("You need to select testCase or test item.")
            return
        self._testManager.runSingleTestPartially(testId, partialMode)
        self._updateReimportRerunButtonEnabled()

    def _clearFilter(self):
        self._searchLE.clear()

    def reload(self, keepUiStates=True):
        self._beforeTestCollection()
        with uistream.LogCaptureContext():  # Report the possible error report to UI as well:
            self._view.reload(keepUiStates=keepUiStates)

        self._updateRunButtonsEnabled()

        if not self._testManager.startDirOrModule():
            return

        self._statusLbl.reportTestCount(self._view.testCount())

    def _applyCurrentFilter(self, removeStateFilters=True, keepUiStates=True):
        searchText = self._searchLE.text()
        if removeStateFilters:
            keywords = searchText.split(" ")
            filterFunc = lambda x: not x.startswith(":")
            keywords = filter(filterFunc, keywords)
            searchText = " ".join(keywords)
            self._searchLE.setText(searchText)

        self._applyFilterTextWithState(searchText, keepUiStates=keepUiStates)

    def _updateRunButtonsEnabled(self):
        enabled = self._view.hasTests()
        self._resetAllBtn.setEnabled(enabled)
        self._runAllBtn.setEnabled(enabled)
        self._viewSelectionChanged()
        self._updateReimportRerunButtonEnabled()

    def _beforeTestCollection(self):
        self._logWgt.onTestStart()
        self._statusLbl.startCollectingTests()

    def _beforeRunningTests(self, tests):
        self._logWgt.onTestStart()
        self._view.resetTestItemsById(tests)

    def _applyFilterText(self, txt):
        self._applyFilterTextWithState(txt, keepUiStates=False)

    def _applyFilterTextWithState(self, txt, keepUiStates=True):
        lowerTxt = txt.strip().lower()
        keywords = lowerTxt.split(" ")
        self._clearFilterBtn.setEnabled(bool(keywords))
        self._view.setFilterKeywords(keywords, ensureFirstMatchVisible=not keepUiStates)

    # These below are to be called by hooks -------------------------------------------------
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
    manager = IUTestWindow()
    manager.show()
