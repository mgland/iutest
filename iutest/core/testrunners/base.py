import logging
from iutest.core.testrunners import runnerconstants

logger = logging.getLogger(__name__)


class TestRunInfo(object):
    def __init__(self):
        self.lastRunTestIds = []
        self.lastFailedTest = None
        self.lastRunTime = 0
        self.lastRunCount = 0
        self.lastSuccessCount = 0
        self.lastFailedCount = 0
        self.lastErrorCount = 0
        self.lastSkipCount = 0
        self.lastExpectedFailureCount = 0
        self.lastUnexpectedSuccessCount = 0


class BaseTestRunner(object):
    def __init__(self, manager):
        self._manager = manager

    @classmethod
    def isDummy(cls):
        return False

    @classmethod
    def isValid(cls):
        return False

    @classmethod
    def check(cls):
        if cls.isValid():
            logger.info("Switch to test runner mode: %s", cls.name())
        else:
            logger.warning(
                "The test runner mode %s is unavailable, you need to install the package first.",
                cls.name(),
            )

    @classmethod
    def mode(cls):
        cls._raiseNotImplementedError()

    @classmethod
    def name(cls):
        return runnerconstants.RUNNER_NAMES[cls.mode()]

    @classmethod
    def icon(cls):
        cls._raiseNotImplementedError()

    @classmethod
    def disabledIcon(cls):
        cls._raiseNotImplementedError()

    @classmethod
    def _raiseNotImplementedError(cls):
        raise NotImplementedError(
            "You should not use {} directly.".format(cls.__name__)
        )

    def runTests(self, *testIds):
        self._raiseNotImplementedError()

    def runSingleTestPartially(self, testId, partialMode):
        """Run partial steps of test, like running setUp only, or setUp and test but without teardown.
        Args:
            testId (str): id of test, the python module.
            partialMode (int): the test run mode, available values are:
                constants.RUN_TEST_SETUP_ONLY | constants.RUN_TEST_NO_TEAR_DOWN
        """
        self._raiseNotImplementedError()

    def iterAllTestIds(self, startDir, topDir):
        self._raiseNotImplementedError()

    @classmethod
    def lastListerError(cls):
        pass

    @classmethod
    def lastRunInfo(cls):
        return TestRunInfo()

    @classmethod
    def lastRunTestIds(cls):
        return cls.lastRunInfo().lastRunTestIds

    @classmethod
    def lastFailedTestIds(cls):
        return cls.lastRunInfo().lastFailedTest

    @classmethod
    def parseParameterizedTestId(cls, testId):
        return False, testId

    @classmethod
    def sourcePathAndLineFromModulePath(cls, modulePath):
        return None, 0
