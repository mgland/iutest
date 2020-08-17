import logging
import time
import sys
from unittest import runner

from iutest.core import constants
from iutest.core import uistream
from iutest.plugins.pyunitextentions import pyunitcommon

logger = logging.getLogger(__name__)

class PyUnitTestRunnerWrapper(runner.TextTestRunner):
    def __init__(
        self, 
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


class PyUnitTestResult(runner.TextTestResult, pyunitcommon.PyUnitUiMixin):
    """A test result class that can show text results in ui, both in tree view and the log browser.
    """
    _originalStdOut = sys.stdout
    _originalStdErr = sys.stderr
    def __init__(self, stream, descriptions, verbosity):
        self.Cls = self.__class__
        self.Base = super(PyUnitTestResult, self)
        self.Base.__init__(stream, descriptions, verbosity)
        pyunitcommon.PyUnitUiMixin.__init__(self, stream)

    def startTestRun(self):
        self._atStartTestRun()
        self.Base.startTestRun()

    def startTest(self, test):
        self._atStartTest(test)
        with self.stream.linkInfoCtx(self._linkInfoFromTest(test)):            
            self.Base.startTest(test)

        self._startLogProcessers()
    
    def stopTest(self, test):
        self.Base.stopTest(test)
        self._atStopTest(test)

    def stopTestRun(self):
        self.Base.stopTestRun()
        self._atStopTestRun()
        resultCode = constants.TEST_RESULT_PASS if self.wasSuccessful() \
            else constants.TEST_RESULT_ERROR
        self.stream.setResult(resultCode)

    def addSuccess(self, test):
        with self.stream.resultCtx(constants.TEST_RESULT_PASS):
            self.Base.addSuccess(test)
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
