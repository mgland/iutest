import logging
from nose2 import result

from iutest.core import constants
from iutest.core import pyunitutils

logger = logging.getLogger(__name__)


# To-Do: Refactor both PyUnitTestResult and similar class in nose2plugs.
# To-Do: Merge ViewUpdater and TestUiLoggerPlugin
class ViewUpdater(object):
    """This class is a set of nose2 event hooks for updating the tests tree view.
    """

    lastRunTestIds = []
    lastRunCount = 0
    lastErrorCount = 0
    lastFailedCount = 0
    lastExpectedFailureCount = 0
    lastSkipCount = 0
    lastSuccessCount = 0
    lastUnexpectedSuccessCount = 0
    lastFailedTest = None

    runTime = 0
    _startTime = 0

    _testRunStartTimes = {}
    def __init__(self, ui):
        self.Cls = self.__class__
        self._ui = ui

    def callUiMethod(self, method, *args, **kwargs):
        if not self._ui:
            return
        method = getattr(self._ui, method)
        if not method:
            logger.error("%s has no method called %s", self._ui, method)
            return
        method(*args, **kwargs)

    def startTestRun(self, event):
        self.callUiMethod(
            "repaintUi"
        )  # To avoid double clicking to run single test will end up massive selection.
        self.Cls.lastFailedTest = None
        self.Cls._startTime = event.startTime
        self.Cls._testRunStartTimes = {}
        self.callUiMethod("onTestRunningSessionStart")

    def stopTestRun(self, event):
        self.Cls.runTime = event.stopTime - self.Cls._startTime
        self.callUiMethod("onAllTestsFinished")

    def startTest(self, event):
        self.Cls.lastRunCount += 1
        originalTestId = event.test.id()
        self.Cls._testRunStartTimes[originalTestId] = event.startTime
        _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
        if testId not in self.Cls.lastRunTestIds:
            self.Cls.lastRunTestIds.append(testId)
            self.callUiMethod("onSingleTestStartToRun", testId, event.startTime)

    def stopTest(self, event):
        testId = event.test.id()
        self.callUiMethod("onSingleTestStop", testId, event.stopTime)
        self.callUiMethod("repaintUi")
        testStartTime = self.Cls._testRunStartTimes.get(testId, self.Cls._startTime)
        self.Cls.runTime = event.stopTime - testStartTime
        
    def testOutcome(self, event):
        testId = event.test.id()
        if event.outcome == result.ERROR:
            self.Cls.lastErrorCount += 1
            if not self.lastFailedTest:
                self.Cls.lastFailedTest = testId
            self.callUiMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_ERROR
            )

        elif event.outcome == result.FAIL:
            if not event.expected:
                self.Cls.lastFailedCount += 1
            else:
                self.Cls.lastExpectedFailureCount += 1
            if not self.lastFailedTest:
                self.Cls.lastFailedTest = testId
            self.callUiMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_FAILED
            )

        elif event.outcome == result.SKIP:
            self.Cls.lastSkipCount += 1
            self.callUiMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_SKIPPED
            )

        elif event.outcome == result.PASS:
            if event.expected:
                self.Cls.lastSuccessCount += 1
            else:
                self.Cls.lastUnexpectedSuccessCount += 1

            self.callUiMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_SUCCESS
            )

    @classmethod
    def resetLastData(cls):
        cls.lastRunTestIds = []
        cls.lastRunCount = 0
        cls.lastErrorCount = 0
        cls.lastFailedCount = 0
        cls.lastExpectedFailureCount = 0
        cls.lastSkipCount = 0
        cls.lastSuccessCount = 0
        cls.lastUnexpectedSuccessCount = 0

    @classmethod
    def getHooks(cls, manager):
        hook = cls(manager)
        return [
            ("startTestRun", hook),
            ("startTest", hook),
            ("stopTest", hook),
            ("stopTestRun", hook),
            ("testOutcome", hook),
        ]
