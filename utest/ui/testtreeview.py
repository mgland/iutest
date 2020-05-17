import logging

from utest.qt import QtCore, QtGui, QtWidgets
from utest.core import iconutils
from utest.core import constants
from utest.core import pathutils
from utest.plugins import testlister
from utest.plugins import viewupdater

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


class TestTreeView(QtWidgets.QTreeWidget):
    runAllTest = QtCore.Signal()
    runTests = QtCore.Signal(list)

    _testAllIcons = []
    _testPackageIcons = []
    _testModuleIcons = []
    _testCaseIcons = []
    _testItemIcons = []
    _allItemIconSet = []

    def __init__(self, parent):
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.setColumnCount(2)
        self._setHeaderStretch()
        self.setHeaderHidden(True)
        self.setAlternatingRowColors(True)
        self.setExpandsOnDoubleClick(False)
        self.setSelectionMode(self.ExtendedSelection)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)

        self._rootTestItem = None
        self._testItems = []
        self._allItemsIdMap = {}
        self._initAllIcons()

        self._testManager = None
        self._viewStates = ViewStates(self)

    def setTestManager(self, manager):
        self._testManager = manager

    def _setHeaderStretch(self):
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, header.Stretch)
        header.setSectionResizeMode(1, header.ResizeToContents)
        header.resizeSection(1, 10)

    def onItemDoubleClicked(self, item, *_, **__):
        if item is self._rootTestItem:
            self.runAllTest.emit()
            return

        self.runTests.emit([self.testIdOfItem(item)])

    @classmethod
    def _initComboIcons(cls, iconVarName, iconFileName):
        iconPaths = iconutils.iconPathSet(iconFileName)
        icons = []
        for path in iconPaths:
            icons.append(QtGui.QIcon(path))
        setattr(cls, iconVarName, icons)

    @classmethod
    def _initAllIcons(cls):
        if cls._allItemIconSet:
            return

        cls._initComboIcons("_testAllIcons", "all.svg")
        cls._initComboIcons("_testPackageIcons", "package.svg")
        cls._initComboIcons("_testModuleIcons", "module.svg")
        cls._initComboIcons("_testCaseIcons", "testCase.svg")
        cls._initComboIcons("_testItemIcons", "testItem.svg")
        cls._allItemIconSet = (
            cls._testAllIcons,
            cls._testPackageIcons,
            cls._testModuleIcons,
            cls._testCaseIcons,
            cls._testItemIcons,
        )

    def setFilterKeywords(self, keywords):
        itemStates = {}
        if keywords:
            needHighlight = len(keywords) > 3
            itemToFocus = None
            for item in self._testItems:
                self._accumulateItemVisibility(item, keywords, itemStates)
                if needHighlight and not itemToFocus and itemStates[item]:
                    itemToFocus = item

            # self._debugItemVisStates(itemStates)

            for index in range(self._rootTestItem.childCount()):
                self._recursivelySetItemVisibility(
                    self._rootTestItem.child(index), itemStates, state=None
                )

            if itemToFocus:
                self.setCurrentItem(itemToFocus)
                self.scrollToItem(itemToFocus)
        else:
            for index in range(self._rootTestItem.childCount()):
                self._recursivelySetItemVisibility(
                    self._rootTestItem.child(index), itemStates, state=True
                )

    def _recursivelySetItemVisibility(self, item, itemStates, state=None):
        visible = state
        if state is None:
            visible = itemStates.get(item, True)

        if not visible:
            item.setHidden(True)
            return

        item.setHidden(False)
        for index in range(item.childCount()):
            self._recursivelySetItemVisibility(item.child(index), itemStates, state)

    def _itemMatchs(self, item, keywords):
        state = item.data(0, QtCore.Qt.UserRole + 1)
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

        itemStates.setdefault(item, state)
        if state:
            itemStates[item] = state
        else:
            state = self._itemMatchs(item, keywords)
            itemStates[item] = itemStates[item] or state
            state = itemStates[item]

        self._accumulateItemVisibility(item.parent(), keywords, itemStates, state=state)

    def _debugItemVisStates(self, states):
        for item in sorted(states.keys()):
            print(self.testIdOfItem(item), states[item])

    def _setItemIconState(self, item, state):
        category = item.data(0, QtCore.Qt.UserRole)
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
        for item in self._testItems:
            self._resetItem(item, False)

    def _resetItem(self, item, applyToAllChildren=False):
        item.setText(1, "")
        if item.data(1, QtCore.Qt.UserRole):
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
            state = max(state, item.child(i).data(0, QtCore.Qt.UserRole + 1))
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

    def copyFirstSelectedTestId(self):
        for item in self.selectedItems():
            if item is self._rootTestItem:
                continue
            QtGui.QGuiApplication.clipboard().setText(self.testIdOfItem(item))

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
            
        self._testItems = []
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

            testItem = cParent
            testItem.setData(0, QtCore.Qt.UserRole, constants.ITEM_CATEGORY_TEST)
            self._setItemIconState(testItem, constants.TEST_ICON_STATE_NORMAL)
            self._testItems.append(cParent)

            caseItem = testItem.parent()
            caseItem.setData(0, QtCore.Qt.UserRole, constants.ITEM_CATEGORY_CASE)
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

    def onSingleTestStartToRun(self, testId, startTime):
        isParameterized, testId = testlister.parseParameterizedTestId(testId)
        item = self._findItemById(testId)
        if item:
            self.focusItem(item)
            self._setTestIconStateToAncestors(item, constants.TEST_ICON_STATE_RUNNING)
            if not isParameterized or not item.data(1, QtCore.Qt.UserRole):
                item.setData(1, QtCore.Qt.UserRole, startTime)
                item.setText(1, "running...")

    def onSingleTestStop(self, testId, endTime):
        _, testId = testlister.parseParameterizedTestId(testId)
        item = self._findItemById(testId)
        if item:
            startTime = item.data(1, QtCore.Qt.UserRole)
            item.setData(1, QtCore.Qt.UserRole + 1, endTime)
            rep = "%.3f s" % (endTime - startTime)
            item.setText(1, rep)

    def showResultOnItemByTestId(self, testId, state):
        _, testId = testlister.parseParameterizedTestId(testId)
        item = self._findItemById(testId)
        if item:
            # For parameterized test, some might succeed but others might failed, we make sure
            # we set failed for this situation.
            if state == constants.TEST_ICON_STATE_SKIPPED or state > item.data(
                0, QtCore.Qt.UserRole + 1
            ):
                self._setItemIconState(item, state)

    def onAllTestsFinished(self):
        lastRunIds = viewupdater.ViewUpdater.lastRunTestIds
        updatedIds = set()

        lastFailedItem = None

        for testId in lastRunIds:
            item = self._findItemById(testId)
            if not item:
                continue

            self._calculateAncestorItemStates(item.parent(), updatedIds)
            if viewupdater.ViewUpdater.lastFailedTest == testId:
                lastFailedItem = item

        self.focusItem(lastFailedItem)

    def testCount(self):
        return len(self._testItems)

    def hasTests(self):
        return bool(self._testItems)

    def runSelectedTests(self):
        itemsByModulePath = {}
        for item in self.selectedItems():
            if item is self._rootTestItem:
                self.runAllTest.emit()
                return

            itemsByModulePath[self.testIdOfItem(item)] = item

        lastKey = None
        testsToRun = []
        for key in sorted(itemsByModulePath.keys()):
            if lastKey and (key).startswith(lastKey):
                continue

            lastKey = key + "."
            logger.debug("Running test: %s", key)
            testsToRun.append(key)

        self.runTests.emit(testsToRun)
