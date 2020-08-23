import logging
from iutest.core.runners import base
from iutest.core.runners import runnerconstants

logger = logging.getLogger(__name__)


class PyTestTestRunner(base.BaseTestRunner):
    # To-Do: Implement this class
    @classmethod
    def mode(cls):
        return runnerconstants.RUNNER_PYTEST

    @classmethod
    def isValid(cls):
        # To-Do: Enable it when it is ready.
        # return dependencies.PyTestWrapper.get().isValid()
        return False

    @classmethod
    def iconFileName(cls):
        return "pytest.svg"

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
        return iter([])
