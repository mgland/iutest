import logging

from iutest import dcc
from iutest import _version
from iutest.core import importutils
from iutest.qt import QtCore, QtGui, QtWidgets, iconFromPath, variantToPyValue
from iutest.core import iconutils
from iutest.core import appsettings
from iutest.core import constants
from iutest.core import testmanager
from iutest.core import uistream
from iutest.ui import logbrowser
from iutest.ui import rootpathedit
from iutest.ui import unittesttree
from iutest.ui import statuslabel
from iutest.ui import uiutils
from iutest.ui import configwindow
from iutest.ui import inlinebuttonlineedit as btnLineEdit

logger = logging.getLogger(__name__)


class IUTestWindow(QtWidgets.QWidget):
    _iutestIcon = None
    _reimportIcon = None
    _reloadUiIcon = None
    _filterIcon = None
    _autoFilterIcon = None
    _resetIcon = None
    _clearLogOnRunIcon = None
    _clearLogIcon = None
    _stopAtErrorIcon = None
    _configIcon = None
    _caseSensitiveIcon = None
    _wholeWordIcon = None
    _panelStateIconSet = None

    def __init__(self, startDirOrModule=None, topDir=None, parent=None):
        parent = parent or dcc.findParentWindow()
        QtWidgets.QWidget.__init__(self, parent)
        self._uiStream = uistream.UiStream()

        self._initIcons()

        self._testManager = testmanager.TestManager(self, startDirOrModule, topDir)

        self._mainLay = uiutils.makeMainLayout(self)
        self.setContentsMargins(0, 0, 0, 0)

        # Top layout ------------------------------
        self._dirLayout = uiutils.makeMinorHorizontalLayout()
        self._testRunnerActions = []
        self._makeDirWidgets()
        self._mainLay.addLayout(self._dirLayout)

        self._splitter = QtWidgets.QSplitter(self)
        self._mainLay.addWidget(self._splitter, 1)

        # left layout -----------------------------------
        self._leftWidget, leftLay = self._createSplitterContent()

        _topLayout = uiutils.makeMinorHorizontalLayout()
        self._makeTreeTopWidgets(_topLayout)
        leftLay.addLayout(_topLayout)

        self._view = unittesttree.UnitTestTreeView(self)
        self._view.runAllTest.connect(self._runAllTests)
        self._view.runTests.connect(self._runTests)
        self._view.runSetupOnly.connect(self._runTestSetupOnly)
        self._view.runWithoutTearDown.connect(self._runTestWithoutTearDown)
        self._view.itemSelectionChanged.connect(self._viewSelectionChanged)

        leftLay.addWidget(self._view)

        # right layout -----------------------------------
        self._rightWidget, rightLay = self._createSplitterContent()
        _logTopLayout = uiutils.makeMinorHorizontalLayout()
        self._logBrowser = logbrowser.LogBrowser(self)
        self._makeLogBrowserTopWidgets(_logTopLayout)
        rightLay.addLayout(_logTopLayout, 0)
        rightLay.addWidget(self._logBrowser, 1)

        self._splitter.setSizes([230, 500])
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)

        # bottom -----------------------------------
        self._statusLbl = statuslabel.StatusLabel(self)
        self._mainLay.addWidget(self._statusLbl)

        _btmLayout = uiutils.makeMinorHorizontalLayout()
        self._makeRunButtons(_btmLayout)
        self._mainLay.addLayout(_btmLayout)

        self.resize(QtCore.QSize(900, 500))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)  # for reimport convenience.
        self.setTabOrder(self._rootDirLE, self._treeFilterLE)
        self.setTabOrder(self._treeFilterLE, self._view)
        self.setTabOrder(self._view, self._logBrowser)
        self.setWindowIcon(self._iutestIcon)
        self.setWindowFlags(QtCore.Qt.Window)

        self._updateWindowTitle()
        self._loadLastDirsFromSettings()
        self._restorePanelVisState()

        self.resetUiTestManager()

        QtCore.QTimer.singleShot(0, self._initialLoad)

    def getLogBrowserWidget(self):
        return self._logBrowser

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

    def _makeLogBrowserTopWidgets(self, layout):
        _console = QtWidgets.QLabel("Log Browser")

        self._logSearchLE = btnLineEdit.InlineButtonLineEdit(withClearButton=True, parent=self)
        self._logSearchLE.setToolTip(
            "Search text in the test history."
        )
        self._logSearchLE.setPlaceholderText("Input to search")
        self._logSearchLE.returnPressed.connect(self._applyLoggingSearchText)

        self._wholeWordBtn = uiutils.makeIconButton(self._wholeWordIcon)
        self._wholeWordBtn.setCheckable(True)
        self._logSearchLE.addButton("wholeWord", self._wholeWordBtn)

        self._sensitiveBtn = uiutils.makeIconButton(self._caseSensitiveIcon)
        self._sensitiveBtn.setCheckable(True)
        self._logSearchLE.addButton("caseSensitive", self._sensitiveBtn)

        self._clearLogBtn = uiutils.makeIconButton(self._clearLogIcon, self)
        self._clearLogBtn.setToolTip("Clear the log browser logging.")
        self._clearLogBtn.clicked.connect(self._logBrowser.clear)

        layout.addWidget(_console, 0)
        layout.addStretch(1)
        layout.addWidget(self._logSearchLE, 0)
        layout.addWidget(self._clearLogBtn, 0)

    def _applyLoggingSearchText(self):
        keyword = str(self._logSearchLE.text())
        if not keyword:
            return

        ctrl = bool(QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ControlModifier)
        flag = QtGui.QTextDocument.FindFlags()
        if self._wholeWordBtn.isChecked():
            flag = flag | QtGui.QTextDocument.FindWholeWords
        if self._sensitiveBtn.isChecked():
            flag = flag | QtGui.QTextDocument.FindCaseSensitively
        if ctrl:
            flag = flag | QtGui.QTextDocument.FindBackward

        found = self._logBrowser.find(keyword, flag)
        if found:
            return
        if not ctrl:
            self._logBrowser.moveCursor(QtGui.QTextCursor.Start)
        else:
            self._logBrowser.moveCursor(QtGui.QTextCursor.End)
        self._logBrowser.find(keyword, flag)

    @classmethod
    def _initSingleIcon(cls, iconVarName, iconFileName):
        iconPath = iconutils.iconPath(iconFileName)
        setattr(cls, iconVarName, iconFromPath(iconPath))

    @classmethod
    def _initIcons(cls):
        if cls._panelStateIconSet:
            return

        panelStatePaths = iconutils.iconPathSet(
            "panelMode.svg", constants.PANEL_VIS_STATE_ICON_SUFFIXES
        )
        cls._panelStateIconSet = [iconFromPath(p) for p in panelStatePaths]

        iconutils.initSingleClassIcon(cls, "_iutestIcon", "iutest.svg")
        iconutils.initSingleClassIcon(cls, "_reimportIcon", "reimport.svg")
        iconutils.initSingleClassIcon(cls, "_reloadUiIcon", "reloadUI.svg")
        iconutils.initSingleClassIcon(cls, "_configIcon", "config.svg")
        iconutils.initSingleClassIcon(cls, "_moreIcon", "more.svg")
        iconutils.initSingleClassIcon(cls, "_filterIcon", "stateFilter.svg")
        iconutils.initSingleClassIcon(cls, "_autoFilterIcon", "autoFilter.svg")
        iconutils.initSingleClassIcon(cls, "_resetIcon", "reset.svg")
        iconutils.initSingleClassIcon(cls, "_clearLogIcon", "clearLog.svg")
        iconutils.initSingleClassIcon(cls, "_clearLogOnRunIcon", "clearLogOnRun.svg")
        iconutils.initSingleClassIcon(cls, "_stopAtErrorIcon", "stopAtError.svg")
        iconutils.initSingleClassIcon(cls, "_caseSensitiveIcon", "caseSensitive.svg")
        iconutils.initSingleClassIcon(cls, "_wholeWordIcon", "wholeWord.svg")

    def _addToggleConfigAction(self, lbl, icon, tooltip, configKey, slot):
        # Cannot use self._configMenu.addAction() directly here since over-zealous garbage collection in some DCC apps:
        act = QtWidgets.QAction(lbl, self)
        act.setIcon(icon)
        act.setCheckable(True)
        act.setToolTip(tooltip)
        act.toggled.connect(slot)
        value = appsettings.get().simpleConfigBoolValue(configKey)
        act.setChecked(value)
        self._configMenu.addAction(act)
        return (act, value)

    def _updateLabelOfTestRunnerAct(self, act, currentMode):
        runnerMode = variantToPyValue(act.data())
        runner = self._testManager.getRunnerByMode(runnerMode)
        suffix = " [actived]" if runnerMode == currentMode else ""
        lbl = runner.name() + suffix
        act.setText(lbl)

    def _updateConfigButton(self, runner):
        self._runnerConfigBtn.setIcon(runner.icon())
        self._runnerConfigBtn.setToolTip(
            "Test Runner: {}, click for more settings.".format(runner.name())
        )

    def _makeRunnerConfigButton(self):
        currentRunner = self._setInitialTestMode()
        currentRunnerMode = currentRunner.mode()
        self._runnerConfigBtn, self._configMenu = uiutils.makeMenuToolButton(parent=self)
        self._updateConfigButton(currentRunner)

        for runner in self._testManager.iterAllRunners():
            icon = runner.icon()
            toolTip = "Run tests using {}.".format(runner.name())
            runnerMode = runner.mode()
            act = QtWidgets.QAction(runner.name(), self)
            act.setIcon(icon)
            act.setEnabled(runner.isValid())
            act.setToolTip(toolTip)
            act.setData(runnerMode)
            act.triggered.connect(self._onTestRunnerSwitched)
            self._updateLabelOfTestRunnerAct(act, currentRunnerMode)
            self._testRunnerActions.append(act)
            self._configMenu.addAction(act)

        self._configMenu.addSeparator()

        # Stop on error act:
        self._stopOnErrorAct, stopOnError = self._addToggleConfigAction(
            "Stop On Error",
            self._stopAtErrorIcon,
            "Stop the tests running once it encounters a test error/failure.",
            configKey=constants.CONFIG_KEY_STOP_ON_ERROR,
            slot=self._onStopOnErrorActionToggled,
        )
        self._testManager.setStopOnError(stopOnError)

        # auto filer on run act:
        self._autoFilterAct, stopOnError = self._addToggleConfigAction(
            "Only Show Tests that Run",
            self._autoFilterIcon,
            "Apply a ':ran' filter automatically after every test run so that only the run tests shown in the view.",
            configKey=constants.CONFIG_KEY_AUTO_FILTERING_STATE,
            slot=self._onAutoFilterActionToggled,
        )

        # auto clear log on run act:
        self._clearLogOnRunAct, stopOnError = self._addToggleConfigAction(
            "Clear LogBrowser On Run",
            self._clearLogOnRunIcon,
            "Clear the log browser automatically before every test run.",
            configKey=constants.CONFIG_KEY_AUTO_CLEAR_LOG_STATE,
            slot=self._onAutoClearLogActionToggled,
        )

        self._configMenu.addSeparator()
        act = self._configMenu.addAction("Preference..")
        act.setIcon(self._configIcon)
        act.triggered.connect(self._showConfigWindow)

    def _showConfigWindow(self):
        configwindow.ConfigWindow.show(self)

    def _setInitialTestMode(self):
        initRunnerMode = appsettings.get().simpleConfigIntValue(
            constants.CONFIG_KEY_LAST_RUNNER_MODE, -1
        )
        if initRunnerMode < 0:
            initRunnerMode = self._testManager.getFeasibleRunnerMode()

        self._testManager.setRunnerMode(initRunnerMode)
        return self._testManager.getRunner()

    def _makeDirWidgets(self):
        lbl = QtWidgets.QLabel("Test Root")
        lbl.setToolTip(
            "Input a python module path or an absolute dir path in the lineEdit for the tests."
        )
        self._rootDirLE = rootpathedit.RootPathEdit(self)
        self._rootDirLE.rootPathChanged.connect(self._switchToTestRootPath)
        self._rootDirLE.rootDirPicked.connect(self._onBrowseTestsRootDir)
        self._rootDirLE.topDirPicked.connect(self._onBrowseTopDir)
        self._rootDirLE.saveCurrentDirSettings.connect(self._onSaveCurrentDirSettings)
        self._rootDirLE.loadSavedDirPair.connect(self._loadSavedDirPair)
        self._rootDirLE.deleteCurrentDirSettings.connect(self._onDeleteCurrentDirSettings)

        self._panelVisBtn = uiutils.makeIconButton(self._panelStateIconSet[-1], self)
        self._panelVisBtn.setToolTip(
            "Switch the test tree view and the log browser visibility."
        )
        self._panelVisBtn.clicked.connect(self._onPanelVisButtonClicked)
        self._makeRunnerConfigButton()

        self._dirLayout.addWidget(lbl)
        self._dirLayout.addWidget(self._rootDirLE)
        self._dirLayout.addWidget(self._panelVisBtn)
        self._dirLayout.addWidget(self._runnerConfigBtn)

        self._updateDirUI()

    def _makeTreeTopWidgets(self, layout):
        reimportBtn = uiutils.makeIconButton(self._reimportIcon, self)
        reimportBtn.setVisible(importutils.isReimportFeatureAvailable(silentCheck=True))
        reimportBtn.setToolTip("Reimport all changed python module.")
        reimportBtn.clicked.connect(self._reimportAllChangedModules)
        layout.addWidget(reimportBtn)

        reloadUIBtn = uiutils.makeIconButton(self._reloadUiIcon, self)
        reloadUIBtn.setToolTip("Recollect tests and reload the test tree view below.")
        reloadUIBtn.clicked.connect(self._onReloadUiButtonClicked)
        layout.addWidget(reloadUIBtn)

        self._treeFilterLE = btnLineEdit.InlineButtonLineEdit(withClearButton=True, parent=self)
        self._treeFilterLE.setToolTip(
            "Input keywords to filter the tests, separated by space.\n"
            "For normal keyword, the match operation is 'AND'\n"
            "For state keyword starting with ':', the match operation is 'OR'."
        )
        self._treeFilterLE.setPlaceholderText("Input to filter")
        self._treeFilterLE.textChanged.connect(self._applyTreeFilterText)
        layout.addWidget(self._treeFilterLE)

        self._filterBtn, self._filterMenu = uiutils.makeMenuToolButton(
            self._filterIcon, "Click to apply more predefined filters.", self
        )
        for lbl in constants.KEYWORD_TEST_STATES:
            act = self._filterMenu.addAction(lbl)
            act.triggered.connect(self._addStateFilter)
        layout.addWidget(self._filterBtn)

    def _onAutoFilterActionToggled(self, state):
        appsettings.get().saveSimpleConfig(
            constants.CONFIG_KEY_AUTO_FILTERING_STATE, state
        )

    def _onAutoClearLogActionToggled(self, state):
        appsettings.get().saveSimpleConfig(
            constants.CONFIG_KEY_AUTO_CLEAR_LOG_STATE, state
        )

    def _onTestRunnerSwitched(self):
        act = self.sender()
        if not act:
            return

        runnerMode = variantToPyValue(act.data())
        self._testManager.setRunnerMode(runnerMode)
        runner = self._testManager.getRunner()
        self._updateConfigButton(runner)

        self._uiStream.write(
            ">> Switch to unittest runner <b>{}</b>.<br>".format(runner.name())
        )

        self._onReloadUiButtonClicked()
        appsettings.get().saveSimpleConfig(
            constants.CONFIG_KEY_LAST_RUNNER_MODE, runnerMode
        )
        for act in self._testRunnerActions:
            self._updateLabelOfTestRunnerAct(act, runnerMode)

    def _onStopOnErrorActionToggled(self, stop):
        self._testManager.setStopOnError(stop)
        appsettings.get().saveSimpleConfig(constants.CONFIG_KEY_STOP_ON_ERROR, stop)

    def _makeRunButtons(self, _btmLayout):
        self._resetAllBtn = uiutils.makeIconButton(self._resetIcon, self)
        self._resetAllBtn.setToolTip(
            "Reset the test item states, icons and stats and collapse the tree view items in a certain level."
        )
        self._resetAllBtn.clicked.connect(self._view.resetAllItemsToNormal)
        _btmLayout.addWidget(self._resetAllBtn, 1)

        self._runSelectedBtn = QtWidgets.QPushButton("Run &Selected", self)
        self._runSelectedBtn.setToolTip("Run the selected tests in the view.")
        self._runSelectedBtn.clicked.connect(self._runViewSelectedTests)
        self._runSelectedBtn.setIcon(self._view._runSelectedIcon)
        _btmLayout.addWidget(self._runSelectedBtn, 1)

        self._runAllBtn = QtWidgets.QPushButton("Run &All", self)
        self._runAllBtn.setToolTip(
            "Run all the tests, including those filtered from the view."
        )
        self._runAllBtn.setIcon(self._view._runAllIcon)
        self._runAllBtn.clicked.connect(self._runAllTests)
        _btmLayout.addWidget(self._runAllBtn, 1)

        self._reimportAndRerunBtn = QtWidgets.QPushButton("&Reload && Rerun", self)
        self._reimportAndRerunBtn.setToolTip(
            "Reimport all changed python modules and rerun the last tests."
        )
        self._reimportAndRerunBtn.clicked.connect(self._reimportPyAndRerun)
        self._reimportAndRerunBtn.setIcon(self._view._reimportAndRunIcon)
        _btmLayout.addWidget(self._reimportAndRerunBtn, 1)

        _runMoreBtn = self._makeRunMoreButton()
        _btmLayout.addWidget(_runMoreBtn, 0)

    def _makeRunMoreButton(self):
        _runMoreBtn = QtWidgets.QToolButton(self)
        _runMoreBtn.setIcon(self._view._runPartialIcon)
        _runMoreBtn.setAutoRaise(True)
        _runMoreBtn.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        _runMoreBtn.setPopupMode(_runMoreBtn.InstantPopup)

        self._runSetupAct = QtWidgets.QAction("Run setUp( ) Only", self)
        self._runSetupAct.setIcon(self._view._runPartialIcon)
        self._runSetupAct.triggered.connect(self._runTestSetupOnly)

        self._runNoTearDown = QtWidgets.QAction("Run without tearDown( )", self)
        self._runNoTearDown.setIcon(self._view._runPartialIcon)
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
        stateKeyword = str(self.sender().text())
        search = str(self._treeFilterLE.text()).strip()
        if not search:
            self._treeFilterLE.setText(stateKeyword)
            return
        parts = search.split(" ")
        if stateKeyword in parts:
            return
        parts.insert(0, stateKeyword)
        self._treeFilterLE.setText(" ".join(parts))

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

        configName = str(act.text())
        self._saveLastTestDir(_startDirOrModule, _topDir)
        self._updateWindowTitle(configName)
        self._updateDirUI()
        self._treeFilterLE.clear()
        self.reload()

    def _switchToTestRootPath(self, startDir, topDir):
        self._testManager.setDirs(startDir, topDir)
        self._updateWindowTitle(startDir)
        self._updateDirUI()
        self._treeFilterLE.clear()
        self.reload(keepUiStates=False)
        if not self._testManager.hasLastListerError():
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

    def _onBrowseTestsRootDir(self, dirPath):
        self._testManager.setStartDirOrModule(dirPath)
        self._updateDirUI()
        self._treeFilterLE.clear()
        self.reload()

    def _onBrowseTopDir(self, dirPath):
        self._testManager.setTopDir(dirPath)

        self._treeFilterLE.clear()
        self._updateDirUI()
        self.reload()

    def _updateWindowTitle(self, configName=None):
        if configName:
            self.setWindowTitle(
                "{} {} - {}".format(
                    constants.APP_NAME, _version.__version__, configName
                )
            )
        else:
            self.setWindowTitle(
                "{} {}".format(constants.APP_NAME, _version.__version__)
            )

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
        QtCore.QTimer.singleShot(0, self._rootDirLE.regenerateBrowseMenu)

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
        self._treeFilterLE.clear()
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
        self._runTests(self._view.selectedTestIds(decomposePackageIfNecessary=True))

    def _updateReimportRerunButtonEnabled(self):
        self._reimportAndRerunBtn.setEnabled(bool(self._testManager.lastRunTestIds()))

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
        testId = self._view.firstSelectedTestCaseId()
        if not testId:
            logger.error("You need to select test suite or test case.")
            return
        self._testManager.runSingleTestPartially(testId, partialMode)
        self._updateReimportRerunButtonEnabled()

    def reload(self, keepUiStates=True):
        self._beforeTestCollection()
        with uistream.LogCaptureContext():  # Report the possible error report to UI as well:
            self._view.reload(keepUiStates=keepUiStates)

        self._updateRunButtonsEnabled()

        if not self._testManager.startDirOrModule():
            return

        self._statusLbl.reportTestCount(self._view.testCount())

    def _applyCurrentFilter(self, removeStateFilters=True, keepUiStates=True):
        searchText = str(self._treeFilterLE.text())
        if removeStateFilters:
            keywords = searchText.split(" ")
            filterFunc = lambda x: not x.startswith(":")
            keywords = filter(filterFunc, keywords)
            searchText = " ".join(keywords)
            self._treeFilterLE.setText(searchText)

        self._applyFilterTextWithState(searchText, keepUiStates=keepUiStates)

    def _updateRunButtonsEnabled(self):
        enabled = self._view.hasTests()
        self._resetAllBtn.setEnabled(enabled)
        self._runAllBtn.setEnabled(enabled)
        self._viewSelectionChanged()
        self._updateReimportRerunButtonEnabled()

    def _hookUiToStream(self):
        uistream.UiStream.setUi(self)

    def _beforeTestCollection(self):
        self._hookUiToStream()
        self._statusLbl.startCollectingTests()

    def _beforeRunningTests(self, tests):
        self._hookUiToStream()
        self._view.resetTestItemsById(tests)

    def _applyTreeFilterText(self, txt):
        self._applyFilterTextWithState(str(txt), keepUiStates=False)

    def _applyFilterTextWithState(self, txt, keepUiStates=True):
        lowerTxt = txt.strip().lower()
        keywords = lowerTxt.split(" ")
        self._view.setFilterKeywords(keywords, ensureFirstMatchVisible=not keepUiStates)

    def closeEvent(self, event):
        uistream.UiStream.unsetUi(self)
        QtWidgets.QWidget.closeEvent(self, event)

    # These below are to be called by hooks -------------------------------------------------
    def onSingleTestStart(self, testId, startTime):
        self._hookUiToStream()
        self._view.onSingleTestStart(testId, startTime)

    def onSingleTestStop(self, testId, endTime):
        self._view.onSingleTestStop(testId, endTime)
        self._statusLbl.updateReport()

    def showResultOnItemByTestId(self, testId, state):
        self._view.showResultOnItemByTestId(testId, state)

    def onTestRunningSessionStart(self):
        self._statusLbl.setText("Running tests...")
        if self._clearLogOnRunAct.isChecked():
            self._logBrowser.clear()
        self._logBrowser.logSeparator()

    def onAllTestsFinished(self):
        self._view.onAllTestsFinished()
        if self._autoFilterAct.isChecked():
            self._treeFilterLE.setText(constants.KEYWORD_TEST_STATE_RUN)
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
