import logging
from nose2 import result

from iutest.core import constants
from iutest.core import runinfo
from iutest.core import pyunitutils

logger = logging.getLogger(__name__)


# To-Do: Refactor both PyUnitTestResult and similar class in nose2plugs.
# To-Do: Merge ViewUpdater and TestUiLoggerPlugin
class ViewUpdater(object):
    """This class is a set of nose2 event hooks for updating the tests tree view.
    """
    lastRunInfo = runinfo.TestRunInfo()
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
        self.Cls.lastRunInfo.failedTestId = None
        self.Cls.lastRunInfo._sessionStartTime = event.startTime
        self.Cls.lastRunInfo._testStartTimes = {}
        self.callUiMethod("onTestRunningSessionStart")

    def stopTestRun(self, event):
        self.Cls.lastRunInfo.sessionRunTime = event.stopTime - self.Cls.lastRunInfo._sessionStartTime
        self.callUiMethod("onAllTestsFinished")

    def startTest(self, event):
        self.Cls.lastRunInfo.runCount += 1
        originalTestId = event.test.id()
        self.Cls.lastRunInfo._testStartTimes[originalTestId] = event.startTime
        _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
        if testId not in self.Cls.lastRunInfo.runTestIds:
            self.Cls.lastRunInfo.runTestIds.append(testId)
            self.callUiMethod("onSingleTestStart", testId, event.startTime)

    def stopTest(self, event):
        testId = event.test.id()
        self.callUiMethod("onSingleTestStop", testId, event.stopTime)
        self.callUiMethod("repaintUi")
        testStartTime = self.Cls.lastRunInfo._testStartTimes.get(testId, self.Cls.lastRunInfo._sessionStartTime)
        self.Cls.singleTestRunTime = event.stopTime - testStartTime
        
    def testOutcome(self, event):
        testId = event.test.id()
        if event.outcome == result.ERROR:
            self.Cls.lastRunInfo.errorCount += 1
            if not self.lastRunInfo.failedTestId:
                self.Cls.lastRunInfo.failedTestId = testId
            self.callUiMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_ERROR
            )

        elif event.outcome == result.FAIL:
            if not event.expected:
                self.Cls.lastRunInfo.failedCount += 1
            else:
                self.Cls.lastRunInfo.expectedFailureCount += 1
            if not self.lastRunInfo.failedTestId:
                self.Cls.lastRunInfo.failedTestId = testId
            self.callUiMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_FAILED
            )

        elif event.outcome == result.SKIP:
            self.Cls.lastRunInfo.skipCount += 1
            self.callUiMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_SKIPPED
            )

        elif event.outcome == result.PASS:
            if event.expected:
                self.Cls.lastRunInfo.successCount += 1
            else:
                self.Cls.lastRunInfo.unexpectedSuccessCount += 1

            self.callUiMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_SUCCESS
            )

    @classmethod
    def resetLastData(cls):
        cls.lastRunInfo.reset()

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
