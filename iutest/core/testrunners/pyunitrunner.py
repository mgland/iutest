from iutest.core import constants
import logging
import os
import unittest
from unittest import loader, suite
from unittest import main as runPyUnittest
from iutest.core import pathutils
from iutest.core import runinfo
from iutest.core.testrunners import base
from iutest.core.testrunners import runnerconstants
from iutest.plugins.pyunitextentions import wrappers

logger = logging.getLogger(__name__)


class PyUnitRunner(base.BaseTestRunner):
    _Icon = None
    _Runner = None
    _lastTests = {}
    _gotError = False

    _loadTestsFailure = "_FailedTest"
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
        self._runTests(constants.RUN_TEST_FULL, *testIds)
        
    def _runTests(self, partialMode=constants.RUN_TEST_FULL, *testIds):
        failfast = self._manager.stopOnError()
        argv = [""]
        argv.extend(testIds)
        wrappers.PyUnitTestResult.resetLastData()
        testRunner = wrappers.PyUnitTestRunnerWrapper(
            self._manager.ui(), 
            failfast=failfast,
            partialMode=partialMode
        )
        runPyUnittest(
            None, 
            argv=argv,
            testRunner=testRunner,
            exit=False, 
            failfast=failfast, 
        )
        testRunner.resetUiStreamResult()

    def runSingleTestPartially(self, testId, partialMode):
        self._runTests(partialMode, testId)

    def _collectAllPaths(self, tests):
        if isinstance(tests, suite.TestSuite):
            for t in tests:
                for p in self._collectAllPaths(t):
                    yield p
        else:
            if not self._isTestFailedToLoad(tests):
                self.__class__._gotError = True
                return

            self._lastTests[tests.id()] = tests
            yield tests.id()

    @classmethod
    def _resetLastTests(cls):
        cls._lastTests = {}

    def _isTestFailedToLoad(self, test):
        if test.__class__.__name__ == self._loadTestsFailure:
            modulename = test.id().split(self._loadTestsFailure)[-1][1:]
            raiser = getattr(test, modulename, None)
            if not raiser:
                return True
            try:
                raiser()
            except Exception:
                logger.exception("Unable to load tests from directory %s", modulename)
                return False

        return True

    def iterAllTestIds(self):
        self.__class__._gotError = False
        self._resetLastTests()
        startDirOrModule = self._manager.startDirOrModule()
        startModule = pathutils.objectFromDotPath(startDirOrModule, silent=True)
        topDir = self._manager.topDir()
        if not topDir or not os.path.isdir(topDir):
            if os.path.isdir(startDirOrModule):
                topDir = startDirOrModule
            elif startModule:
                topDir = os.path.dirname(startModule.__file__)

        tests = loader.defaultTestLoader.discover(startDirOrModule, top_level_dir=topDir)
        if not startModule:
            for p in self._collectAllPaths(tests):
                yield p
        else:
            for p in self._collectAllPaths(tests):
                if not p.startswith(startDirOrModule):
                    yield ".".join([startDirOrModule, p])

    @classmethod
    def haslastListerError(cls):
        return cls._gotError

    @classmethod
    def lastRunInfo(cls):
        return wrappers.PyUnitTestResult.lastRunInfo
    
    @classmethod
    def avoidRunTestsOnPackageLevel(self):
        """PyUnit is difficult to run test from package level without discovering it.
        """
        return True
