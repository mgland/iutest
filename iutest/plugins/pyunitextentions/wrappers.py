import logging
import time
import sys
from unittest import runner

from iutest.core import constants
from iutest.core import pyunitutils
from iutest.core import uistream
from iutest.core import pathutils
from iutest.core import runinfo

logger = logging.getLogger(__name__)

class PyUnitTestRunnerWrapper(runner.TextTestRunner):
    def __init__(
        self, 
        testWindow, 
        verbosity=2, 
        failfast=False, 
        partialMode=constants.RUN_TEST_FULL
        ):
        self._verbosity = verbosity
        self.stream = uistream.UiStream()
        self._partialMode = partialMode

        # call baseClass.__init__() here means running the test:
        runner.TextTestRunner.__init__(
            self, 
            stream=self.stream,
            resultclass=PyUnitTestResult,
            verbosity=verbosity, 
            failfast=failfast)
    
    @staticmethod
    def _dummyFunction(*_, **__):
        pass
    
    def resetUiStreamResult(self):
        self.stream.setResult()

    def _getTestCaseFromTest(self, test):
        while not hasattr(test, "id"):
            tests = list(test)
            if not tests:
                logger.error("No test to run.")
                return
            test = tests[0]
            
        return test

    def run(self, test):
        # If we run test partially, we guarante that suite only contains a single testCase object.
        if self._partialMode != constants.RUN_TEST_FULL:
            test = self._getTestCaseFromTest(test)
            test.tearDown = self._dummyFunction
            if self._partialMode == constants.RUN_TEST_SETUP_ONLY:
                methodName = test.id().split(".")[-1]
                setattr(test, methodName, self._dummyFunction)
                logger.info("Run %s.setUp() only:", test.__class__.__name__)

            elif self._partialMode == constants.RUN_TEST_NO_TEAR_DOWN:
                logger.info("Skipped %s.tearDown():", test.__class__.__name__)

        return runner.TextTestRunner.run(self, test)


# To-Do: Refactor both PyUnitTestResult and similar class in nose2plugs.
class PyUnitTestResult(runner.TextTestResult):
    """A test result class that can show text results in ui, both in tree view and the log browser.
    """
    lastRunInfo = runinfo.TestRunInfo()

    _originalStdOut = sys.stdout
    _originalStdErr = sys.stderr
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

    def _callUiMethod(self, method, *args, **kwargs):
        if hasattr(self.stream, "callUiMethod"):
            self.stream.callUiMethod(method, *args, **kwargs)

    @classmethod
    def _recordLastFailedTestId(cls, testId):
        if not cls.lastRunInfo.failedTestId:
            cls.lastRunInfo.failedTestId = testId

    def _atOutcomeAvailable(self, testId, resultCode):
        iconState = constants.TEST_ICON_STATE_SUCCESS
        if resultCode == constants.TEST_RESULT_ERROR:
            self.Cls.lastRunInfo.errorCount += 1
            self._recordLastFailedTestId(testId)
            iconState = constants.TEST_ICON_STATE_ERROR

        elif resultCode == constants.TEST_RESULT_FAIL:
            iconState = constants.TEST_ICON_STATE_FAILED
            self.Cls.lastRunInfo.failedCount += 1
            self._recordLastFailedTestId(testId)

        elif resultCode == constants.TEST_RESULT_EXPECTED_FAIL:
            iconState = constants.TEST_ICON_STATE_FAILED
            self.Cls.lastRunInfo.expectedFailureCount += 1
            self._recordLastFailedTestId(testId)

        elif resultCode == constants.TEST_RESULT_SKIP:
            self.Cls.lastRunInfo.skipCount += 1
            iconState = constants.TEST_ICON_STATE_SKIPPED

        elif resultCode == constants.TEST_RESULT_PASS:
            iconState = constants.TEST_ICON_STATE_SUCCESS
            self.Cls.lastRunInfo.successCount += 1

        elif resultCode == constants.TEST_RESULT_UNEXPECTED_PASS:
            self.Cls.lastRunInfo.unexpectedSuccessCount += 1
            iconState = constants.TEST_ICON_STATE_SUCCESS                

        self._callUiMethod(
                "showResultOnItemByTestId", testId, iconState
            )
        self.stdOutCapturer.stop()
        self.stdErrCapturer.stop()
        self.logHandler.stop()

    def startTestRun(self):
        self._callUiMethod(
            "repaintUi"
        )  # To avoid double clicking to run single test will end up massive selection.
        self.Cls.lastRunInfo.failedTestId = None
        self.Cls.lastRunInfo._sessionStartTime = time.time()
        self.Cls.lastRunInfo._testStartTimes = {}
        self._callUiMethod("onTestRunningSessionStart")
        self.Base.startTestRun()

    def stopTestRun(self):
        self.Base.stopTestRun()
        self.Cls.lastRunInfo.sessionRunTime = time.time() - self.Cls.lastRunInfo._sessionStartTime
        self._callUiMethod("onAllTestsFinished")

        resultCode = constants.TEST_RESULT_PASS if self.wasSuccessful() \
            else constants.TEST_RESULT_ERROR
        self.stream.setResult(resultCode)

    def startTest(self, test):
        info = self._linkInfoFromTest(test)
        with self.stream.linkInfoCtx(info):
            self.Cls.lastRunInfo.runCount += 1
            
            originalTestId = test.id()
            _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
            if testId not in self.Cls.lastRunInfo.runTestIds:
                testStartTime = time.time()
                self.Cls.lastRunInfo._testStartTimes[testId] = testStartTime
                self.Cls.lastRunInfo.runTestIds.append(testId)
                self._callUiMethod("onSingleTestStart", testId, testStartTime)

            self.Base.startTest(test)

        self.logHandler.start()
        self.stdOutCapturer.start()
        self.stdErrCapturer.start()
    
    def stopTest(self, test):
        self.Base.stopTest(test)
        originalTestId = test.id()
        _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
        stopTime = time.time()
        testStartTime = self.Cls.lastRunInfo._testStartTimes.get(testId, self.Cls.lastRunInfo._sessionStartTime)
        self.Cls.lastRunInfo.singleTestRunTime = stopTime - testStartTime
        
        self._callUiMethod("onSingleTestStop", testId, stopTime)
        self._callUiMethod("repaintUi")

    @classmethod
    def resetLastData(cls):
        cls.lastRunInfo.reset()

    def addSuccess(self, test):
        with self.stream.resultCtx(constants.TEST_RESULT_PASS):
            self.Base.addSuccess(test)
            self.Cls.lastRunInfo.successCount += 1
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