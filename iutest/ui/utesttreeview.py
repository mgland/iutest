import logging

from iutest.qt import QtCore, QtGui, QtWidgets, Signal, variantToPyValue, iconFromPath
from iutest.core import iconutils
from iutest.core import constants
from iutest.core import pathutils
from iutest.core import gotocode
from iutest.core import importutils
from iutest.core import loggingutils

logger = logging.getLogger(__name__)


class ViewStates(object):
    def __init__(self, testTreeView):
        self._treeWidget = testTreeView
        self.reset()

    def reset(self):
        self._currentItemId = None
        self._itemExpandStates = {}
        self._horizontalScrollValue = 0
        self._verticalScrollValue = 0

    def save(self):
        if not self._treeWidget:
            return

        self.reset()
        currentItem = self._treeWidget.currentItem()
        if currentItem:
            self._currentItemId = self._treeWidget.testIdOfItem(currentItem)

        for testId, item in self._treeWidget.allItemsIdMap().items():
            self._itemExpandStates[testId] = item.isExpanded()
        self._horizontalScrollValue = self._treeWidget.horizontalScrollBar().value()
        self._verticalScrollValue = self._treeWidget.verticalScrollBar().value()

    def _restoreScrollValue(self):
        self._treeWidget.horizontalScrollBar().setValue(self._horizontalScrollValue)
        self._treeWidget.verticalScrollBar().setValue(self._verticalScrollValue)

    def restore(self):
        if not self._treeWidget:
            return
        itemIdMap = self._treeWidget.allItemsIdMap()
        cItem = itemIdMap.get(self._currentItemId, None)
        if cItem:
            self._treeWidget.setCurrentItem(cItem)
        for testId, expand in self._itemExpandStates.items():
            item = itemIdMap.get(testId, None)
            if item:
                item.setExpanded(expand)
        QtCore.QTimer.singleShot(0, self._restoreScrollValue)


class UTestTreeView(QtWidgets.QTreeWidget):
    runAllTest = Signal()
    runTests = Signal(list)
    runSetupOnly = Signal(str)
    runWithoutTearDown = Signal(str)

    _testAllIcons = []
    _testPackageIcons = []
    _testModuleIcons = []
    _testSuiteIcons = []
    _testCaseIcons = []
    _allItemIconSet = []

    supportPartialCategories = (
        constants.ITEM_CATEGORY_SUITE,
        constants.ITEM_CATEGORY_TEST,
    )

    class _TreeItemDelegate(QtWidgets.QItemDelegate):
        def drawFocus(self, painter, styleOptionViewItem, rect):
            pass

    def __init__(self, parent):
        QtWidgets.QTreeWidget.__init__(self, parent)
        self._codeVisitor = gotocode.CodeLineVisitor(self)

        self.setItemDelegate(self._TreeItemDelegate(self))
        self.setTextElideMode(QtCore.Qt.ElideLeft)
        self.setColumnCount(2)
        self._setHeaderStretch()
        self.setHeaderHidden(True)
        self.setAlternatingRowColors(True)
        self.setExpandsOnDoubleClick(False)
        self.setSelectionMode(self.ExtendedSelection)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.setIndentation(10)

        self._rootTestItem = None
        self._testCases = []
        self._allItemsIdMap = {}
        self._initAllIcons()

        self._testManager = None
        self._viewStates = ViewStates(self)

        self._contextMenu = QtWidgets.QMenu(self)
        self._makeContextMenu()

        self.setToolTip(
            "This view lists out the tests, <b>double click</b> on them to run them, <b>Ctrl+C</b> to copy the python module path."
        )

    def setTestManager(self, manager):
        self._testManager = manager

    def _setHeaderStretch(self):
        header = self.header()
        header.setStretchLastSection(False)
        if hasattr(header, "setSectionResizeMode"):
            header.setSectionResizeMode(0, header.Stretch)
            header.setSectionResizeMode(1, header.ResizeToContents)
        else:
            header.setResizeMode(0, header.Stretch)
            header.setResizeMode(1, header.ResizeToContents)

        header.resizeSection(1, 10)

    def _iterAllDescendentItem(self, parentItem, category):
        for i in range(parentItem.childCount()):
            item = parentItem.child(i)
            if self._categoryOfItem(item) == category:
                yield item
                continue

            for it in self._iterAllChildrenItem(item, category):
                yield it

    def _splitPackageTestIds(self, *testIds):
        if not self._testManager.avoidRunTestsOnPackageLevel():
            return tuple(testIds)

        items = filter(None, [self._findItemById(tid) for tid in testIds])
        return self._splitPackageTestItems(*items)

    def _splitPackageTestItems(self, *items):
        if not self._testManager.avoidRunTestsOnPackageLevel():
            return tuple([self.testIdOfItem(item) for item in items])

        testIds = []
        for item in items:
            if self._categoryOfItem(item) != constants.ITEM_CATEGORY_PACKAGE:
                testIds.append(self.testIdOfItem(item))
                continue
            
            splittedTests = [self.testIdOfItem(item) for item in \
                self._iterAllDescendentItem(item, constants.ITEM_CATEGORY_MODULE)]
            testIds.extend(splittedTests)
        return tuple(testIds)

    def onItemDoubleClicked(self, item, *_, **__):
        if item is self._rootTestItem:
            self.runAllTest.emit()
            return

        self.runTests.emit(self._splitPackageTestItems(item))

    @classmethod
    def _initComboIcons(cls, iconVarName, iconFileName):
        iconPaths = iconutils.iconPathSet(iconFileName, constants.TEST_ICON_SUFFIXES)
        icons = []
        for path in iconPaths:
            icons.append(iconFromPath(path))
        setattr(cls, iconVarName, icons)

    @classmethod
    def _initAllIcons(cls):
        if cls._allItemIconSet:
            return

        cls._initComboIcons("_testAllIcons", "all.svg")
        cls._initComboIcons("_testPackageIcons", "package.svg")
        cls._initComboIcons("_testModuleIcons", "module.svg")
        cls._initComboIcons("_testSuiteIcons", "testSuite.svg")
        cls._initComboIcons("_testCaseIcons", "testCase.svg")
        cls._allItemIconSet = (
            cls._testAllIcons,
            cls._testPackageIcons,
            cls._testModuleIcons,
            cls._testSuiteIcons,
            cls._testCaseIcons,
        )

    def setFilterKeywords(self, keywords, ensureFirstMatchVisible=False):
        itemStates = {}
        if keywords:
            itemToFocus = None
            for item in self._testCases:
                self._accumulateItemVisibility(item, keywords, itemStates)
                if not itemToFocus:
                    itemToFocus = item

            # self._debugItemVisStates(itemStates)

            for index in range(self._rootTestItem.childCount()):
                self._recursivelySetItemVisibility(
                    self._rootTestItem.child(index), itemStates, state=None
                )

            if itemToFocus and ensureFirstMatchVisible:
                self.focusItem(itemToFocus)
        else:
            for index in range(self._rootTestItem.childCount()):
                self._recursivelySetItemVisibility(
                    self._rootTestItem.child(index), itemStates, state=True
                )

    def _recursivelySetItemVisibility(self, item, itemStates, state=None):
        visible = state
        stateKey = self.testIdOfItem(item)
        if state is None:
            visible = itemStates.get(stateKey, True)

        if not visible:
            item.setHidden(True)
            return

        item.setHidden(False)
        for index in range(item.childCount()):
            self._recursivelySetItemVisibility(item.child(index), itemStates, state)

    def _itemMatchs(self, item, keywords):
        state = variantToPyValue(item.data(0, QtCore.Qt.UserRole + 1))
        stateMatch = False
        txtMatch = True
        lbl = self.testIdOfItem(item).lower()
        hasFilter = False
        for each in keywords:
            if not each.startswith(":"):
                if each not in lbl:
                    return False

            if each.startswith(":"):
                hasFilter = True
                if not stateMatch:
                    desiredState = constants.TEST_ICON_STATE_NORMAL
                    if each in constants.KEYWORD_TEST_STATES:
                        desiredState = constants.KEYWORD_TEST_STATES[each]
                    if desiredState < 0:
                        stateMatch = state > 0
                    else:
                        stateMatch = state == desiredState

        stateMatch = stateMatch or not hasFilter
        return stateMatch and txtMatch

    def _accumulateItemVisibility(self, item, keywords, itemStates, state=None):
        if not item:
            return

        if item is self._rootTestItem:
            return

        stateKey = self.testIdOfItem(item)
        itemStates.setdefault(stateKey, state)
        if state:
            itemStates[stateKey] = state
        else:
            state = self._itemMatchs(item, keywords)

            itemStates[stateKey] = itemStates[stateKey] or state
            state = itemStates[stateKey]

        self._accumulateItemVisibility(item.parent(), keywords, itemStates, state=state)

    def _debugItemVisStates(self, states):
        for tid in sorted(states.keys()):
            print(tid, states[tid])

    def _categoryOfItem(self, item):
        return variantToPyValue(item.data(0, QtCore.Qt.UserRole))

    def _setItemIconState(self, item, state):
        self._initAllIcons()
        category = self._categoryOfItem(item)
        icons = self._allItemIconSet[category]
        item.setData(0, QtCore.Qt.UserRole + 1, state)
        item.setIcon(0, icons[state])

    def _setTestIconStateToDecendents(self, item, state):
        self._setItemIconState(item, state)
        for i in range(item.childCount()):
            self._setTestIconStateToDecendents(item.child(i), state)

    def _setTestIconStateToAncestors(self, item, state):
        self._setItemIconState(item, state)
        if item is not self._rootTestItem:
            self._setTestIconStateToAncestors(item.parent(), state)

    def resetAllItemsToNormal(self):
        self._setTestIconStateToDecendents(
            self._rootTestItem, constants.TEST_ICON_STATE_NORMAL
        )
        self._resetExpandStates(self._rootTestItem)
        for item in self._testCases:
            self._resetItem(item, False)

    def _resetItem(self, item, applyToAllChildren=False):
        item.setText(1, "")
        if variantToPyValue(item.data(1, QtCore.Qt.UserRole)):
            item.setData(1, QtCore.Qt.UserRole, 0)

        if applyToAllChildren:
            for i in range(item.childCount()):
                self._resetItem(item.child(i), applyToAllChildren)

    def allItemsIdMap(self):
        return self._allItemsIdMap

    def _findItemById(self, testId):
        return self._allItemsIdMap.get(testId, None)

    def resetTestItemsById(self, testIds):
        for tid in testIds:
            item = self._findItemById(tid)
            if not item:
                continue

            self._resetItem(item, True)
            self._setTestIconStateToAncestors(item, constants.TEST_ICON_STATE_NORMAL)
            self._setTestIconStateToDecendents(item, constants.TEST_ICON_STATE_NORMAL)
        self.repaint()

    def focusItem(self, item):
        if item:
            self.clearSelection()
            self.setCurrentItem(item)
            self.scrollToItem(item)

    def _calculateAncestorItemStates(self, item, updatedIds):
        cId = self.testIdOfItem(item)
        if cId in updatedIds:
            return

        updatedIds.add(cId)
        state = constants.TEST_ICON_STATE_NORMAL
        for i in range(item.childCount()):
            state = variantToPyValue(item.child(i).data(0, QtCore.Qt.UserRole + 1))
            state = max(state, state)
        self._setItemIconState(item, state)

        if item is self._rootTestItem:
            return

        self._calculateAncestorItemStates(item.parent(), updatedIds)

    def testIdOfItem(self, item):
        return item.toolTip(0)

    def _resetExpandStates(self, item):
        item.setExpanded(True)
        childCount = item.childCount()
        if childCount == 1:
            self._resetExpandStates(item.child(0))
        else:
            for i in range(childCount):
                item.child(i).setExpanded(False)

    def _firstSelectedModulePath(self):
        for item in self.selectedItems():
            return self.testIdOfItem(item)
        return None

    def copyFirstSelectedTestId(self):
        firstSelectedModulePath = self._firstSelectedModulePath()
        if firstSelectedModulePath:
            QtWidgets.QApplication.clipboard().setText(firstSelectedModulePath)
            logger.info("Module Path copied to clipboard: %s", firstSelectedModulePath)
        else:
            logger.info("No item selected to copy the module path.")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C and (
            event.modifiers() & QtCore.Qt.ControlModifier
        ):
            self.copyFirstSelectedTestId()
            event.accept()
            return

        QtWidgets.QTreeWidget.keyPressEvent(self, event)

    def reload(self, keepUiStates=True):
        if keepUiStates:
            self._viewStates.save()

        self._testCases = []
        self._rootTestItem = None
        self._allItemsIdMap = {}
        self.clear()

        startDirOrModule = self._testManager.startDirOrModule()
        if not startDirOrModule:
            return

        self._rootTestItem = QtWidgets.QTreeWidgetItem([startDirOrModule])
        self._rootTestItem.setToolTip(0, startDirOrModule)
        self._rootTestItem.setData(0, QtCore.Qt.UserRole, constants.ITEM_CATEGORY_ALL)
        self._setItemIconState(self._rootTestItem, constants.TEST_ICON_STATE_NORMAL)
        self.addTopLevelItem(self._rootTestItem)

        self._allItemsIdMap[startDirOrModule] = self._rootTestItem

        isModule = not pathutils.isPath(startDirOrModule)
        headingCount = 0
        heading = ""
        if isModule:
            headingCount = len(startDirOrModule) + 1
            heading = startDirOrModule + "."

        for test in self._testManager.iterAllTestIds():
            if isModule and test.startswith(startDirOrModule):
                test = test[headingCount:]
            testPaths = test.split(".")
            cParent = self._rootTestItem
            for i, p in enumerate(testPaths):
                path = heading + ".".join(testPaths[0 : (i + 1)])
                if path in self._allItemsIdMap:
                    cParent = self._allItemsIdMap[path]
                    continue

                item = QtWidgets.QTreeWidgetItem(cParent)
                item.setText(0, p)
                item.setToolTip(0, path)
                item.setSizeHint(0, QtCore.QSize(20, 20))
                self._allItemsIdMap[path] = item
                cParent = item

            testCase = cParent
            testCase.setData(0, QtCore.Qt.UserRole, constants.ITEM_CATEGORY_TEST)
            self._setItemIconState(testCase, constants.TEST_ICON_STATE_NORMAL)
            self._testCases.append(cParent)

            caseItem = testCase.parent()
            caseItem.setData(0, QtCore.Qt.UserRole, constants.ITEM_CATEGORY_SUITE)
            self._setItemIconState(caseItem, constants.TEST_ICON_STATE_NORMAL)

            moduleItem = caseItem.parent()
            moduleItem.setData(0, QtCore.Qt.UserRole, constants.ITEM_CATEGORY_MODULE)
            self._setItemIconState(moduleItem, constants.TEST_ICON_STATE_NORMAL)

            packageItem = moduleItem.parent()
            while packageItem is not self._rootTestItem and packageItem:
                packageItem.setData(
                    0, QtCore.Qt.UserRole, constants.ITEM_CATEGORY_PACKAGE
                )
                self._setItemIconState(packageItem, constants.TEST_ICON_STATE_NORMAL)
                packageItem = packageItem.parent()

        if keepUiStates:
            self._viewStates.restore()
        else:
            self._resetExpandStates(self._rootTestItem)

    def onSingleTestStart(self, testId, startTime):
        isParameterized, testId = self._testManager.parseParameterizedTestId(testId)
        item = self._findItemById(testId)
        if item:
            self.focusItem(item)
            self._setTestIconStateToAncestors(item, constants.TEST_ICON_STATE_RUNNING)
            if not isParameterized or not variantToPyValue(
                item.data(1, QtCore.Qt.UserRole)
            ):
                item.setData(1, QtCore.Qt.UserRole, startTime)
                item.setText(1, "running...")

    def onSingleTestStop(self, testId, endTime):
        _, testId = self._testManager.parseParameterizedTestId(testId)
        item = self._findItemById(testId)
        if item:
            startTime = variantToPyValue(item.data(1, QtCore.Qt.UserRole))
            item.setData(1, QtCore.Qt.UserRole + 1, endTime)
            rep = "%.3f s" % (endTime - startTime)
            item.setText(1, rep)

    def showResultOnItemByTestId(self, testId, state):
        _, testId = self._testManager.parseParameterizedTestId(testId)
        item = self._findItemById(testId)
        if item:
            # For parameterized test, some might succeed but others might failed, we make sure
            # we set failed for this situation.
            if state == constants.TEST_ICON_STATE_SKIPPED or state > variantToPyValue(
                item.data(0, QtCore.Qt.UserRole + 1)
            ):
                self._setItemIconState(item, state)

    def onAllTestsFinished(self):
        lastRunIds = self._testManager.lastRunTestIds()
        updatedIds = set()

        lastFailedItem = None

        for testId in lastRunIds:
            item = self._findItemById(testId)
            if not item:
                continue

            self._calculateAncestorItemStates(item.parent(), updatedIds)
            if self._testManager.lastFailedTestId() == testId:
                lastFailedItem = item

        self.focusItem(lastFailedItem)

    def testCount(self):
        return len(self._testCases)

    def hasTests(self):
        return bool(self._testCases)

    def selectedTestIds(self, decomposePackageIfNecessary=False):
        itemsByModulePath = {
            self.testIdOfItem(item): item for item in self.selectedItems()
        }

        lastKey = None
        testsToRun = []
        for key in sorted(itemsByModulePath.keys()):
            if lastKey and (key).startswith(lastKey):
                continue

            lastKey = key + "."
            logger.debug("Running test: %s", key)
            testsToRun.append(key)

        if decomposePackageIfNecessary:
            return self._splitPackageTestIds(*testsToRun)

        return tuple(testsToRun)

    def _iterSelectedSuiteOrTestCaseItems(self):
        for item in self.iterSelectedItemsOfCategories(*self.supportPartialCategories):
            yield item

    def _firstSelectedTestCaseItem(self):
        """Return first selected test case id.
        
        Notes:
            If there is any selected test cases, return the first id. 
            If there isn't but there is selected test suite, return its first test case id.
        """
        for item in self._iterSelectedSuiteOrTestCaseItems():
            if self._categoryOfItem(item) == constants.ITEM_CATEGORY_TEST:
                return item
            
            for i in range(item.childCount()):
                return item.child(i)

        return None

    def firstSelectedTestCaseId(self):
        item = self._firstSelectedTestCaseItem()
        return None if not item else self.testIdOfItem(item)

    def hasSelectedTests(self, hasSelectedTestOrCase=False):
        if not hasSelectedTestOrCase:
            return bool(self.selectionModel().hasSelection())

        return self.hasSelectionOfCategories(*self.supportPartialCategories)

    def hasSelectionOfCategories(self, *categories):
        for item in self.selectedItems():
            if self._categoryOfItem(item) in categories:
                return True
        return False

    def iterSelectedItemsOfCategories(self, *categories):
        for item in self.selectedItems():
            if self._categoryOfItem(item) in categories:
                yield item

    def _makeContextMenu(self):
        self._runSetupOnlyAct = QtWidgets.QAction("Run setUp( ) Only", self)
        self._runSetupOnlyAct.triggered.connect(self._atRunSetupOnly)

        self._runWithoutTearDownAct = QtWidgets.QAction("Run Without tearDown( )", self)
        self._runWithoutTearDownAct.triggered.connect(self._atRunWithoutTearDown)

        self._runSelectedAct = QtWidgets.QAction("Run Selected", self)
        self._runSelectedAct.triggered.connect(self._atRunSelected)

        self._runAllAct = QtWidgets.QAction("Run All", self)
        self._runAllAct.triggered.connect(self._atRunAll)

        self._copyPathAct = QtWidgets.QAction("Copy Selected Path", self)
        self._copyPathAct.triggered.connect(self.copyFirstSelectedTestId)

        self._goToCodeAct = QtWidgets.QAction("Go To Code", self)
        self._goToCodeAct.triggered.connect(self._atGoToCode)

        self._reloadModulesAct = QtWidgets.QAction("Reload Selected Modules", self)
        self._reloadModulesAct.setVisible(importutils.isReimportFeatureAvailable(silentCheck=True))
        self._reloadModulesAct.triggered.connect(self._atReloadSelectedModules)

        self._contextMenu.addAction(self._runAllAct)
        self._contextMenu.addAction(self._runSelectedAct)
        self._contextMenu.addSeparator()

        self._contextMenu.addAction(self._runSetupOnlyAct)
        self._contextMenu.addAction(self._runWithoutTearDownAct)
        self._contextMenu.addSeparator()

        self._contextMenu.addAction(self._copyPathAct)
        self._contextMenu.addAction(self._goToCodeAct)

        self._contextMenu.addSeparator()
        self._contextMenu.addAction(self._reloadModulesAct)

        self._logLevelMenu = QtWidgets.QMenu("Set Logging Level")
        self._contextMenu.addMenu(self._logLevelMenu)
        self._logLevelActionGrp = QtWidgets.QActionGroup(self._logLevelMenu)
        self._logLevelActionGrp.setExclusive(True)

    def _atReloadSelectedModules(self):
        for moduleItem in self.iterSelectedItemsOfCategories(
            constants.ITEM_CATEGORY_MODULE
        ):
            dotPath = self.testIdOfItem(moduleItem)
            importutils.reimportByModulePath(dotPath)

    def _atRunSetupOnly(self):
        testId = self.firstSelectedTestCaseId()
        if testId:
            self.runSetupOnly.emit(testId)

    def _atRunWithoutTearDown(self):
        testId = self.firstSelectedTestCaseId()
        if testId:
            self.runWithoutTearDown.emit(testId)

    def _atRunSelected(self):
        testIds = self.selectedTestIds(decomposePackageIfNecessary=True)
        if testIds:
            self.runTests.emit(testIds)

    def _atRunAll(self):
        self.runAllTest.emit()

    def _atGoToCode(self):
        firstSelectedModulePath = self._firstSelectedModulePath()
        sourceFile, line = pathutils.sourcePathAndLineFromModulePath(
            firstSelectedModulePath
        )
        if sourceFile:
            self._codeVisitor.goTo(sourceFile, line)

    def _setSelectedItemsLevel(self):
        level = variantToPyValue(self.sender().data())
        loggingutils.setLoggingLevel(level, *self.selectedTestIds())

    def contextMenuEvent(self, event):
        gotTests = self.hasTests()
        hasSelection = False
        hasSelectedTestOrCase = False
        hasModuleSelection = False
        if gotTests:
            hasSelection = self.hasSelectedTests(hasSelectedTestOrCase=False)
            hasSelectedTestOrCase = self.hasSelectedTests(hasSelectedTestOrCase=True)
            hasModuleSelection = self.hasSelectionOfCategories(
                constants.ITEM_CATEGORY_MODULE
            )

        self._runSelectedAct.setEnabled(hasSelection)
        self._runSetupOnlyAct.setEnabled(hasSelectedTestOrCase)
        self._runWithoutTearDownAct.setEnabled(hasSelectedTestOrCase)
        self._copyPathAct.setEnabled(hasSelection)
        self._goToCodeAct.setEnabled(hasSelection)
        self._reloadModulesAct.setEnabled(hasModuleSelection)

        self._logLevelMenu.clear()
        levels = loggingutils.loggingLevels(*self.selectedTestIds())
        currentLevel = levels[0] if len(levels) == 1 else None
        for level in loggingutils.allLoggingLevel():
            act = self._logLevelMenu.addAction(logging.getLevelName(level))
            act.setCheckable(True)
            act.setChecked(level == currentLevel)
            self._logLevelActionGrp.addAction(act)
            self._logLevelMenu.addAction(act)
            act.setData(level)
            act.triggered.connect(self._setSelectedItemsLevel)

        self._contextMenu.exec_(event.globalPos())
