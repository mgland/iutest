import logging
from unittest import loader, suite
from iutest.core import pathutils
from iutest.core import pyunitutils
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

    def _collectAllPaths(self, tests):
        if isinstance(tests, suite.TestSuite):
            for t in tests:
                for p in self._collectAllPaths(t):
                    yield p
        else:
            yield tests.id()

    def iterAllTestIds(self):
        startDirOrModule = self._manager.startDirOrModule()
        topDir = self._manager.topDir()
        tests = loader.defaultTestLoader.discover(startDirOrModule, 'test*.py', topDir)

        for p in self._collectAllPaths(tests):
            yield p

    @classmethod
    def lastListerError(cls):
        return None

    @classmethod
    def lastRunInfo(cls):
        info = base.TestRunInfo()
        return info
