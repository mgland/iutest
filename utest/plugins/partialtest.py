import unittest
import logging
import nose2  # This has to be imported this way.

from utest.core import constants

logger = logging.getLogger(__name__)


class _NoTearDown(object):
    def __init__(self, test):
        self._test = test
        self._originalTearDown = test.tearDown
    
    def _dummyTearDown(self):
        logger.info('Skipped %s.tearDown().', self._test.__class__.__name__)

    def __enter__(self):
        self._test.tearDown = self._dummyTearDown

    def __exit__(self, *args, **kwargs):
        self._test.tearDown = self._originalTearDown


class PartialTestRunner(nose2.events.Plugin):
    """A nose2 plug to run parts of single test, like run only setup, setup+test, etc.
    """

    commandLineSwitch = (None, "partial-test", "Run partial test.")
    runMode = constants.RUN_TEST_SETUP_ONLY

    lastRunTest = None
    @classmethod
    def setRunMode(cls, mode):
        """Set run mode to either TEST_SETUP_ONLY or TEST_NO_TEAR_DOWN
        """
        cls.runMode = min(constants.RUN_TEST_NO_TEAR_DOWN, max(constants.RUN_TEST_SETUP_ONLY, int(mode)))
    
    def registerInSubprocess(self, event):
        event.pluginClasses.append(self.__class__)

    def startTestRun(self, event):
        PartialTestRunner.lastRunTest = None 
        event.executeTests = self.runPartialTest

    def startSubprocess(self, event):
        PartialTestRunner.lastRunTest = None 
        event.executeTests = self.runPartialTest
        event.StopTestRunEvent = None
    
    def _runPartialTest(self, test):
        if self.runMode == constants.RUN_TEST_SETUP_ONLY:
            logger.info('Run %s.setUp() only.', test.__class__.__name__)
            test.setUp()
        else:
            with _NoTearDown(test):
                test.run(self.session.testResult)

        PartialTestRunner.lastRunTest = test

    def runPartialTest(self, suite, result):
        """Collect tests, but don't run them"""
        if self.lastRunTest:
            return

        for test in suite:
            if isinstance(test, unittest.BaseTestSuite):
                self.runPartialTest(test, result)
                continue
            
            self._runPartialTest(test)
            return
