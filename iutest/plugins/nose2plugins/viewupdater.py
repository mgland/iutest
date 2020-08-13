import logging
from nose2 import result

from iutest.core import constants
from iutest.core import pyunitutils
from iutest.plugins.nose2plugins import testlister

logger = logging.getLogger(__name__)


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

    def __init__(self, manager):
        self._manager = manager

    def callManagerMethod(self, method, *args, **kwargs):
        if not self._manager:
            return
        method = getattr(self._manager, method)
        if not method:
            logger.error("%s has no method called %s", self._manager, method)
            return
        method(*args, **kwargs)

    def startTestRun(self, event):
        self.callManagerMethod(
            "repaintUi"
        )  # To avoid double clicking to run single test will end up massive selection.
        ViewUpdater.lastFailedTest = None
        ViewUpdater._startTime = event.startTime
        self.callManagerMethod("onTestRunningSessionStart")

    def stopTestRun(self, event):
        ViewUpdater.runTime = event.stopTime - ViewUpdater._startTime
        self.callManagerMethod("onAllTestsFinished")

    def startTest(self, event):
        ViewUpdater.lastRunCount += 1
        originalTestId = event.test.id()
        _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
        if testId not in ViewUpdater.lastRunTestIds:
            ViewUpdater.lastRunTestIds.append(testId)
            self.callManagerMethod("onSingleTestStartToRun", testId, event.startTime)

    def stopTest(self, event):
        testId = event.test.id()
        self.callManagerMethod("onSingleTestStop", testId, event.stopTime)
        self.callManagerMethod("repaintUi")
        ViewUpdater.runTime = event.stopTime - ViewUpdater._startTime

    def testOutcome(self, event):
        testId = event.test.id()
        cls = self.__class__
        if event.outcome == result.ERROR:
            cls.lastErrorCount += 1
            if not self.lastFailedTest:
                ViewUpdater.lastFailedTest = testId
            self.callManagerMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_ERROR
            )

        elif event.outcome == result.FAIL:
            if not event.expected:
                cls.lastFailedCount += 1
            else:
                cls.lastExpectedFailureCount += 1
            if not self.lastFailedTest:
                ViewUpdater.lastFailedTest = testId
            self.callManagerMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_FAILED
            )

        elif event.outcome == result.SKIP:
            cls.lastSkipCount += 1
            self.callManagerMethod(
                "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_SKIPPED
            )

        elif event.outcome == result.PASS:
            if event.expected:
                cls.lastSuccessCount += 1
            else:
                cls.lastUnexpectedSuccessCount += 1

            self.callManagerMethod(
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
