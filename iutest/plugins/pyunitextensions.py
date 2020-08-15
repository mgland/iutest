import logging
import time
import sys
from unittest import runner

from iutest.core import constants
from iutest.core import pyunitutils
from iutest.core import uistream
from iutest.core import pathutils
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

    runTime = 0
    _startTime = 0

    _originalStdOut = sys.stdout
    _originalStdErr = sys.stderr

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
        self.logHandler = uistream.LogHandler()
        self.stdOutCapturer = uistream.StdOutCapturer(self._originalStdOut)
        self.stdErrCapturer = uistream.StdErrCapturer(self._originalStdErr)

    def _linkInfoFromTest(self, test):
        try:
            testMethodName = test.id().split(".")[-1]
            test = getattr(test, testMethodName)
            sourceFile, line = pathutils.sourceFileAndLineFromObject(test)
            if not sourceFile:  # os.path.isfile(sourceFile)
                return None

            return testMethodName, sourceFile, line
        except:
            logger.debug("Unable retrieve test information for quick navigation.")
        return None

    def callUiMethod(self, method, *args, **kwargs):
        if not self._ui:
            return
        method = getattr(self._ui, method)
        if not method:
            logger.error("%s has no method called %s", self._ui, method)
            return
        method(*args, **kwargs)

    @classmethod
    def _recordLastFailedTestId(cls, testId):
        if not cls.lastFailedTest:
            cls.lastFailedTest = testId

    def _atOutcomeAvailable(self, testId, resultCode):
        if resultCode == constants.TEST_RESULT_ERROR:
            self.Cls.lastErrorCount += 1
            self._recordLastFailedTestId(testId)
            iconState = constants.TEST_ICON_STATE_ERROR

        elif resultCode == constants.TEST_RESULT_FAIL:
            iconState = constants.TEST_ICON_STATE_FAILED
            self.Cls.lastFailedCount += 1
            self._recordLastFailedTestId(testId)

        elif resultCode == constants.TEST_RESULT_EXPECTED_FAIL:
            iconState = constants.TEST_ICON_STATE_FAILED
            self.Cls.lastExpectedFailureCount += 1
            self._recordLastFailedTestId(testId)

        elif resultCode == constants.TEST_RESULT_SKIP:
            self.Cls.lastSkipCount += 1
            iconState = constants.TEST_ICON_STATE_SKIPPED

        elif resultCode == constants.TEST_RESULT_PASS:
            iconState = constants.TEST_ICON_STATE_SUCCESS
            self.Cls.lastSuccessCount += 1

        elif resultCode == constants.TEST_RESULT_UNEXPECTED_PASS:
            self.Cls.lastUnexpectedSuccessCount += 1
            iconState = constants.TEST_ICON_STATE_SUCCESS                

        self.callUiMethod(
                "showResultOnItemByTestId", testId, iconState
            )
        self.stdOutCapturer.stop()
        self.stdErrCapturer.stop()
        self.logHandler.stop()

        self._uiStream.setResult(resultCode)
        self._uiStream.setResult()

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
        info = self._linkInfoFromTest(test)
        self._uiStream.setLinkInfo(info)
        self.Cls.lastRunCount += 1
        
        originalTestId = test.id()
        _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
        if testId not in self.Cls.lastRunTestIds:
            testStartTime = time.time()
            self.Cls._testRunStartTimes[testId] = testStartTime
            self.Cls.lastRunTestIds.append(testId)
            self.callUiMethod("onSingleTestStartToRun", testId, testStartTime)

        self.Base.startTest(test)
        
        self._uiStream.setLinkInfo()

        self.logHandler.start()
        self.stdOutCapturer.start()
        self.stdErrCapturer.start()
    
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
        self.Base.addSuccess(test)

        self.Cls.lastSuccessCount += 1
        self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_PASS)

    def addError(self, test, err):
        self.Base.addError(test, err)
        self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_ERROR)

    def addFailure(self, test, err):
        self.Base.addFailure(test, err)
        self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_FAIL)

    def addSkip(self, test, reason):
        self.Base.addSkip(test, reason)
        self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_SKIP)

    def addExpectedFailure(self, test, err):
        self.Base.addExpectedFailure(test, err)
        self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_EXPECTED_FAIL)

    def addUnexpectedSuccess(self, test):
        self.Base.addUnexpectedSuccess(test)
        self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_UNEXPECTED_PASS)
