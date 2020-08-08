import logging
from iutest.core.testrunners import base
from iutest.libs import nose2
from iutest.core import pathutils
from iutest.plugins.nose2plugins import viewupdater
from iutest.plugins.nose2plugins import testlister
from iutest.plugins.nose2plugins import partialtest

logger = logging.getLogger(__name__)

class PyTestTestRunner(base.BaseTestRunner):
    @classmethod
    def name(cls):
        return "pytest"
        
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
