import logging
import time
import sys
from unittest import runner
from unittest.suite import TestSuite

from iutest.core import constants
from iutest.core import pyunitutils
from iutest.core import uistream
from iutest.core import pathutils
from unittest import TestProgram

logger = logging.getLogger(__name__)

class PyUnitTestRunnerWrapper(runner.TextTestRunner):
    def __init__(self, treeView, verbosity=2, failfast=False):
        self._verbosity = verbosity
        self.stream = uistream.UiStream()
        self.stream.setTreeView(treeView)
        runner.TextTestRunner.__init__(
            self, 
            stream=self.stream,
            resultclass=PyUnitTestResult,
            verbosity=verbosity, 
            failfast=failfast)

    def resetUiStreamResult(self):
        self.stream.setResult()


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

    def __init__(self, stream, descriptions, verbosity):
        self.Cls = self.__class__
        self.Base = super(PyUnitTestResult, self)
        self.Base.__init__(
            stream, 
            descriptions, 
            verbosity)
        
        self.stream = stream
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

    def callTreeViewMethod(self, method, *args, **kwargs):
        if hasattr(self.stream, "callTreeViewMethod"):
            self.stream.callTreeViewMethod(method, *args, **kwargs)

    @classmethod
    def _recordLastFailedTestId(cls, testId):
        if not cls.lastFailedTest:
            cls.lastFailedTest = testId

    def _atOutcomeAvailable(self, testId, resultCode):
        iconState = constants.TEST_ICON_STATE_SUCCESS
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

        self.callTreeViewMethod(
                "showResultOnItemByTestId", testId, iconState
            )
        self.stdOutCapturer.stop()
        self.stdErrCapturer.stop()
        self.logHandler.stop()

    def startTestRun(self):
        self.callTreeViewMethod(
            "repaintUi"
        )  # To avoid double clicking to run single test will end up massive selection.
        self.Cls.lastFailedTest = None
        self.Cls._startTime = time.time()
        self.callTreeViewMethod("onTestRunningSessionStart")
        self.Cls._testRunStartTimes = {}
        self.Base.startTestRun()

    def stopTestRun(self):
        self.Base.stopTestRun()
        self.Cls.runTime = time.time() - self.Cls._startTime
        self.callTreeViewMethod("onAllTestsFinished")

        resultCode = constants.TEST_RESULT_PASS if self.wasSuccessful() \
            else constants.TEST_RESULT_ERROR
        self.stream.setResult(resultCode)

    def startTest(self, test):
        info = self._linkInfoFromTest(test)
        with self.stream.linkInfoCtx(info):
            self.Cls.lastRunCount += 1
            
            originalTestId = test.id()
            _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
            if testId not in self.Cls.lastRunTestIds:
                testStartTime = time.time()
                self.Cls._testRunStartTimes[testId] = testStartTime
                self.Cls.lastRunTestIds.append(testId)
                self.callTreeViewMethod("onSingleTestStartToRun", testId, testStartTime)

            self.Base.startTest(test)

        self.logHandler.start()
        self.stdOutCapturer.start()
        self.stdErrCapturer.start()
    
    def stopTest(self, test):
        self.Base.stopTest(test)
        originalTestId = test.id()
        _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
        stopTime = time.time()
        testStartTime = self.Cls._testRunStartTimes.get(testId, self.Cls._startTime)
        self.Cls.runTime = stopTime - testStartTime
        
        self.callTreeViewMethod("onSingleTestStop", testId, stopTime)
        self.callTreeViewMethod("repaintUi")

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
        with self.stream.resultCtx(constants.TEST_RESULT_PASS):
            self.Base.addSuccess(test)
            self.Cls.lastSuccessCount += 1
            self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_PASS)

    def addError(self, test, err):
        with self.stream.resultCtx(constants.TEST_RESULT_ERROR):
            self.Base.addError(test, err)
            self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_ERROR)

    def addFailure(self, test, err):
        with self.stream.resultCtx(constants.TEST_RESULT_FAIL):
            self.Base.addFailure(test, err)
            self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_FAIL)

    def addSkip(self, test, reason):
        with self.stream.resultCtx(constants.TEST_RESULT_SKIP):
            self.Base.addSkip(test, reason)
            self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_SKIP)

    def addExpectedFailure(self, test, err):
        with self.stream.resultCtx(constants.TEST_RESULT_EXPECTED_FAIL):
            self.Base.addExpectedFailure(test, err)
            self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_EXPECTED_FAIL)

    def addUnexpectedSuccess(self, test):
        with self.stream.resultCtx(constants.TEST_RESULT_UNEXPECTED_PASS):
            self.Base.addUnexpectedSuccess(test)
            self._atOutcomeAvailable(test.id(), constants.TEST_RESULT_UNEXPECTED_PASS)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            with self.stream.resultCtx(constants.TEST_RESULT_FAIL): 
                self.stream.writeln(self.separator1)

            with self.stream.linkInfoCtx(self._linkInfoFromTest(test)):
                self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))

            self.stream.writeln(self.separator2)

            with self.stream.processStackTraceLinkCtx():
                self.stream.writeln("%s" % err)
        
        # We set the result code to error, so the summary will be in red.
        if errors:
            self.stream.setResult(constants.TEST_RESULT_ERROR)

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