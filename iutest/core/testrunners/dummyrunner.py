import logging
from iutest.core.testrunners import base
from iutest.core.testrunners import runnerconstants

logger = logging.getLogger(__name__)


class DummyRunner(base.BaseTestRunner):
    @classmethod
    def isDummy(cls):
        return True

    @classmethod
    def icon(cls):
        return None

    @classmethod
    def mode(cls):
        return runnerconstants.RUNNER_DUMMY

    @classmethod
    def _warnNoRunner(cls):
        logger.warning("No test runner installed in system or chosen in UI.")

    def runTests(self, *testIds):
        self._warnNoRunner()

    def runSingleTestPartially(self, testId, partialMode):
        self._warnNoRunner()

    def iterAllTestIds(self):
        self._warnNoRunner()
        return iter([])
