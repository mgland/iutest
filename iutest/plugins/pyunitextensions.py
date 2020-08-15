import logging
import time
from unittest import runner

from iutest.core import constants
from iutest.core import pyunitutils
from iutest.core import uistream
from unittest import TestProgram

logger = logging.getLogger(__name__)

class PyUnitTest(runner.TextTestRunner):
    def __init__(self, ui, verbosity=1, failfast=False):
        self._ui = ui
        self._verbosity = verbosity
        runner.TextTestRunner.__init__(
            self, 
            stream=uistream.UiStream(),
            verbosity=verbosity, 
            failfast=failfast)
    
    def _makeResult(self):
        return PyUnitTestResult(self._ui, verbosity=self._verbosity)


# To-Do: Refactor both PyUnitTestResult and similar class in nose2plugs.
class PyUnitTestResult(runner.TextTestResult):
    """A test result class that can show text results in ui, both in tree view and the log browser.
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

    _testRunStartTimes = {}

    def __init__(self, ui, verbosity=1):
        self.Cls = self.__class__
        self.Base = super(PyUnitTestResult, self)
        self._ui = ui
        self._uiStream = uistream.UiStream()
        self.Base.__init__(
            self._uiStream, 
            "A test result for ui update", 
            verbosity)

    def callUiMethod(self, method, *args, **kwargs):
        if not self._ui:
            return
        method = getattr(self._ui, method)
        if not method:
            logger.error("%s has no method called %s", self._ui, method)
            return
        method(*args, **kwargs)

    def startTestRun(self):
        self.callUiMethod(
            "repaintUi"
        )  # To avoid double clicking to run single test will end up massive selection.
        self.Cls.lastFailedTest = None
        self.Cls._startTime = time.time()
        self.callUiMethod("onTestRunningSessionStart")
        self.Cls._testRunStartTimes = {}
        self.Base.startTestRun()

    def stopTestRun(self):
        self.Base.stopTestRun()
        self.Cls.runTime = time.time() - self.Cls._startTime
        self.callUiMethod("onAllTestsFinished")

    def startTest(self, test):
        self.Cls.lastRunCount += 1
        originalTestId = test.id()
        _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
        if testId not in self.Cls.lastRunTestIds:
            testStartTime = time.time()
            self.Cls._testRunStartTimes[testId] = testStartTime
            self.Cls.lastRunTestIds.append(testId)
            self.callUiMethod("onSingleTestStartToRun", testId, testStartTime)

        self.Base.startTest(test)
    
    def stopTest(self, test):
        self.Base.stopTest(test)
        originalTestId = test.id()
        _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
        stopTime = time.time()
        self.callUiMethod("onSingleTestStop", testId, stopTime)
        self.callUiMethod("repaintUi")
        testStartTime = self.Cls._testRunStartTimes.get(testId, self.Cls._startTime)
        self.Cls.runTime = stopTime - testStartTime

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

    def addSuccess(self, test):
        testId = test.id()

        self.Base.addSuccess(test)

        self.Cls.lastSuccessCount += 1
        self.callUiMethod(
            "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_SUCCESS
        )

    def addError(self, test, err):
        testId = test.id()

        self.Base.addError(test, err)

        self.Cls.lastErrorCount += 1
        if not self.lastFailedTest:
            self.Cls.lastFailedTest = testId
        self.callUiMethod(
            "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_ERROR
        )      

    def addFailure(self, test, err):
        testId = test.id()

        self.Base.addFailure(test, err)

        self.Cls.lastFailedCount += 1
        if not self.lastFailedTest:
            self.Cls.lastFailedTest = testId
        self.callUiMethod(
            "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_FAILED
        )

    def addSkip(self, test, reason):
        testId = test.id()

        self.Base.addSkip(test, reason)

        self.Cls.lastSkipCount += 1
        self.callUiMethod(
            "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_SKIPPED
        )

    def addExpectedFailure(self, test, err):
        testId = test.id()

        self.Base.addExpectedFailure(test, err)

        self.Cls.lastExpectedFailureCount += 1
        if not self.lastFailedTest:
            self.Cls.lastFailedTest = testId
        self.callUiMethod(
            "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_FAILED
        )

    def addUnexpectedSuccess(self, test):
        testId = test.id()

        self.Base.addUnexpectedSuccess(test)

        self.Cls.lastUnexpectedSuccessCount += 1
        self.callUiMethod(
            "showResultOnItemByTestId", testId, constants.TEST_ICON_STATE_SUCCESS
        )
