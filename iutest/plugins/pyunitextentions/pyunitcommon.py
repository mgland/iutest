import sys
import logging
import time

from iutest.core import uistream
from iutest.core import pathutils
from iutest.core import runinfo
from iutest.core import constants
from iutest.core import pyunitutils

logger = logging.getLogger(__name__)

class PyUnitUiMixin(object):
    lastRunInfo = runinfo.TestRunInfo()

    _originalStdOut = sys.stdout
    _originalStdErr = sys.stderr
    
    def __init__(self, stream):
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

    @classmethod
    def resetLastData(cls):
        cls.lastRunInfo.reset()

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

    def _atStartTestRun(self):
        self._callUiMethod(
            "repaintUi"
        )  # To avoid double clicking to run single test will end up massive selection.
        self.Cls.lastRunInfo.failedTestId = None
        self.Cls.lastRunInfo._sessionStartTime = time.time()
        self.Cls.lastRunInfo._testStartTimes = {}
        self._callUiMethod("onTestRunningSessionStart")

    def _startLogProcessers(self):
        self.logHandler.start()
        self.stdOutCapturer.start()
        self.stdErrCapturer.start()

    def _atStartTest(self, test):
        self.Cls.lastRunInfo.runCount += 1
        originalTestId = test.id()
        _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
        if testId not in self.Cls.lastRunInfo.runTestIds:
            testStartTime = time.time()
            self.Cls.lastRunInfo._testStartTimes[testId] = testStartTime
            self.Cls.lastRunInfo.runTestIds.append(testId)
            self._callUiMethod("onSingleTestStart", testId, testStartTime)

    def _atStopTest(self, test):
        originalTestId = test.id()
        _, testId = pyunitutils.parseParameterizedTestId(originalTestId)
        stopTime = time.time()
        testStartTime = self.Cls.lastRunInfo._testStartTimes.get(testId, self.Cls.lastRunInfo._sessionStartTime)
        self.Cls.lastRunInfo.singleTestRunTime = stopTime - testStartTime
        
        self._callUiMethod("onSingleTestStop", testId, stopTime)
        self._callUiMethod("repaintUi")

    def _atStopTestRun(self):
        self.Cls.lastRunInfo.sessionRunTime = time.time() - self.Cls.lastRunInfo._sessionStartTime
        self._callUiMethod("onAllTestsFinished")
