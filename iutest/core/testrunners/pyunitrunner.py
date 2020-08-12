import logging
from iutest.core.testrunners import base
from iutest.core.testrunners import runnerconstants

logger = logging.getLogger(__name__)


class PyUnitRunner(base.BaseTestRunner):
    _Icon = None

    @classmethod
    def isValid(cls):
        return True

    @classmethod
    def mode(cls):
        return runnerconstants.RUNNER_PYUNIT

    @classmethod
    def iconFileName(cls):
        return "unittest.svg"

    def runTests(self, *testIds):
        pass

    def runSingleTestPartially(self, testId, partialMode):
        pass

    def iterAllTestIds(self):
        pass

    @classmethod
    def lastListerError(cls):
        pass

    @classmethod
    def lastRunInfo(cls):
        info = base.TestRunInfo()
        return info

    @classmethod
    def parseParameterizedTestId(cls, testId):
        pass

    @classmethod
    def sourcePathAndLineFromModulePath(cls, modulePath):
        pass
