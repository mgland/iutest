import logging
from iutest.core.testrunners import base

logger = logging.getLogger(__name__)

class DummyRunner(base.BaseTestRunner):
    @classmethod
    def name(cls):
        return "dummy"

    @classmethod
    def _warnNoRunner(cls):
        logger.warning("No test runner installed or picked.")

    def runTests(self, *testIds):
        self._warnNoRunner()

    def runSingleTestPartially(self, testId, partialMode):
        self._warnNoRunner()

    def iterAllTestIds(self):
        pass

    @classmethod
    def lastListerError(cls):
        return None
