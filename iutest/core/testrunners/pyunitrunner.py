import logging
import os
import unittest
from unittest import loader, suite, runner, TestProgram
from iutest.core import pathutils
from iutest.core import pyunitutils
from iutest.core.testrunners import base
from iutest.core.testrunners import runnerconstants

logger = logging.getLogger(__name__)


class PyUnitRunner(base.BaseTestRunner):
    _Icon = None
    _Runner = None
    _lastTests = {}
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
        failfast = self._manager.stopOnError()
        for tid in testIds:
            tester = TestProgram(tid, argv=[''],verbosity=0, exit=False, failfast=failfast)
            tester.createTests()
            tester.runTests()
        
        # if not self._Runner:
        #     self.__class__._Runner = runner.TextTestRunner()

        # self._Runner.failfast = self._manager.stopOnError()
        # startMod = self._manager.startDirOrModule()
        # startIndex = len(startMod) + 1
        # for tid in testIds:
        #     if tid.startswith(startMod):
        #         tid = tid[startIndex:]
        #     testObj = self._lastTests.get(tid)
        #     print("Get:", tid, "=>", testObj)
        #     self._Runner.run(testObj)

    def runSingleTestPartially(self, testId, partialMode):
        pass

    def _collectAllPaths(self, tests):
        if isinstance(tests, suite.TestSuite):
            for t in tests:
                for p in self._collectAllPaths(t):
                    yield p
        else:
            self._lastTests[tests.id()] = tests
            #print("Collect:", tests.id(), "=>", tests)
            yield tests.id()

    @classmethod
    def _resetLastTests(cls):
        cls._lastTests = {}

    def iterAllTestIds(self):
        self._resetLastTests()
        startDirOrModule = self._manager.startDirOrModule()
        topDir = self._manager.topDir()
        if not topDir or not os.path.isdir(topDir):
            if os.path.isdir(startDirOrModule):
                topDir = startDirOrModule
            else:
                module = pathutils.objectFromDotPath(startDirOrModule)
                topDir = os.path.dirname(module.__file__)

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
