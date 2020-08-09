import logging
from iutest import qt as _qt
from iutest import dependencies
from iutest.core import iconutils
from iutest.core.testrunners import base
from iutest.core.testrunners import runnerconstants
from iutest.core import pathutils

logger = logging.getLogger(__name__)

class PyTestTestRunner(base.BaseTestRunner):
    _Icon = None
    _DisabledIcon = None

    # To-Do: Implement this class
    @classmethod
    def name(cls):
        return "pytest"

    def isDummy(self):
        return False

    @classmethod
    def mode(cls):
        return runnerconstants.RUNNER_PYTEST

    @classmethod
    def isValid(cls):
        return dependencies.PyTestWrapper.get().isValid()

    @classmethod
    def icon(cls):
        if not cls._Icon:
            cls._Icon = _qt.iconFromPath(iconutils.iconPath("pytest.svg"))
        return cls._Icon
        
    def runTests(self, *testIds):
        pass

    def runSingleTestPartially(self, testId, partialMode):
        """Run partial steps of test, like running setUp only, or setUp and test but without teardown.
        Args:
            testId (str): id of test, the python module.
            partialMode (int): the test run mode, available values are:
                constants.RUN_TEST_SETUP_ONLY | constants.RUN_TEST_NO_TEAR_DOWN
        """
        pass

    def iterAllTestIds(self):
        pass
