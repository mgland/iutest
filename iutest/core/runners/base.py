import logging
from iutest import qt as _qt
from iutest.core import pyunitutils
from iutest.core import iconutils
from iutest.core import runinfo
from iutest.core.runners import runnerconstants

logger = logging.getLogger(__name__)


class BaseTestRunner(object):
    def __init__(self, manager):
        self._manager = manager

    @classmethod
    def isValid(cls):
        return False

    @classmethod
    def iconFileName(cls):
        cls._raiseNotImplementedError()

    @classmethod
    def icon(cls):
        return _qt.iconFromPath(iconutils.iconPath(cls.iconFileName()))

    @classmethod
    def _issueNotInstalledError(cls):
        logger.warning(
            "The test runner %s is not installed, consider installing it by: `pip install %s`",
            cls.name(), cls.name(),
        )

    @classmethod
    def check(cls):
        if cls.isValid():
            logger.debug("Switch to test runner %s.", cls.name())
        else:
            logger.warning(
                "The test runner %s is unavailable, you need to install it first or switch to other runners.",
                cls.name(),
            )

    @classmethod
    def mode(cls):
        cls._raiseNotImplementedError()

    @classmethod
    def name(cls):
        return runnerconstants.RUNNER_NAMES[cls.mode()]

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
    def hasLastListerError(cls):
        pass

    @classmethod
    def lastRunInfo(cls):
        return runinfo.TestRunInfo()

    @classmethod
    def lastRunTestIds(cls):
        return cls.lastRunInfo().runTestIds

    @classmethod
    def lastFailedTestId(cls):
        return cls.lastRunInfo().failedTestId

    @classmethod
    def parseParameterizedTestId(cls, testId):
        return pyunitutils.parseParameterizedTestId(testId)
    
    @classmethod
    def avoidRunTestsOnPackageLevel(self):
        """A stupid interface to tell the test manager to split these package level test id first.
        """
        return False