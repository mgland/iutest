import unittest
import os
from unittest.suite import TestSuite

from iutest.core import constants
from iutest.core import pathutils
from iutest.core import pyunitutils
from iutest.core import testmanager

from iutest.core.runners import runnerconstants


class RunnerDummyTestCase(unittest.TestCase):
    _setupExecuted = False
    _testExecuted = False
    _tearDownExecuted = False

    def setUp(self):
        self.__class__._setupExecuted = True
        self.__class__._testExecuted = False
        self.__class__._tearDownExecuted = False

    def test_dummy(self):
        self.__class__._testExecuted = True
        self.__class__._tearDownExecuted = False

    def tearDown(self):
        self.__class__._tearDownExecuted = True

    @classmethod
    def checkSetUpRun(cls, testSuite, expectRun):
        testSuite.assertEqual(cls._setupExecuted, expectRun)

    @classmethod
    def checkTestRun(cls, testSuite, expectRun):
        testSuite.assertEqual(cls._testExecuted, expectRun)

    @classmethod
    def checkTearDownRun(cls, testSuite, expectRun):
        testSuite.assertEqual(cls._tearDownExecuted, expectRun)

    @classmethod
    def resetStates(cls, testSuite):
        cls._setupExecuted = False
        cls._testExecuted = False
        cls._tearDownExecuted = False
        cls.checkSetUpRun(testSuite, False)
        cls.checkTestRun(testSuite, False)
        cls.checkTearDownRun(testSuite, False)


def initTestTargets(testSuite):
    testSuite._testId = __name__
    testSuite._modulePath = "iutest.tests"


def setUpTest(testSuite, runnerMode):
    testSuite._manager = testmanager.TestManager(None, None)
    testSuite._manager.setRunnerMode(runnerMode)
    testSuite.assertEqual(testSuite._manager.getRunner().mode(), runnerMode)
    initTestTargets(testSuite)


def checkListedTests(testSuite, tests):
    testSuite.assertTrue(tests)
    hasThisTest = False
    prefix = "iutest.tests.iutests.{}.{}.test_".format(
        os.path.splitext(os.path.basename(__file__))[0], RunnerDummyTestCase.__name__
    )
    for tid in tests:
        if tid.startswith(prefix):
            hasThisTest = True
    testSuite.assertTrue(hasThisTest)


def checkParseParameterizedTestId(testSuite):
    data = {
        "test_mod.TestSuite.test_case": (False, "test_mod.TestSuite.test_case"),
        "test_mod.TestSuite.test_case:34": (True, "test_mod.TestSuite.test_case"),
    }
    for testId, expected in data.items():
        testSuite.assertEqual(pyunitutils.parseParameterizedTestId(testId), expected)


def checkListByDir(testSuite):
    startDir = os.path.join(pathutils.iutestPackageDir(), "tests")
    topDir = pathutils.iutestRootDir()
    testSuite._manager.setDirs(startDir, topDir)

    tests = list(testSuite._manager.iterAllTestIds())
    checkListedTests(testSuite, tests)


def checkListByModulePath(testSuite):
    testSuite._manager.setStartDirOrModule(testSuite._modulePath)

    tests = list(testSuite._manager.iterAllTestIds())
    checkListedTests(testSuite, tests)


def checkRunTestsAfterAction(testSuite, action):
    RunnerDummyTestCase.resetStates(testSuite)
    action()
    RunnerDummyTestCase.checkSetUpRun(testSuite, True)
    RunnerDummyTestCase.checkTestRun(testSuite, True)
    RunnerDummyTestCase.checkTearDownRun(testSuite, True)
    print("The test on {} did run.".format(RunnerDummyTestCase.__name__))


def checkRunTests(testSuite):
    testSuite._manager.setStartDirOrModule(testSuite._modulePath)
    action = lambda: testSuite._manager.runTests(testSuite._testId)
    checkRunTestsAfterAction(testSuite, action)


def checkPartialRun(testSuite):
    RunnerDummyTestCase.resetStates(testSuite)
    testSuite._manager.setStartDirOrModule(testSuite._modulePath)

    testSuite._manager.runSingleTestPartially(
        testSuite._testId, constants.RUN_TEST_SETUP_ONLY
    )
    RunnerDummyTestCase.checkSetUpRun(testSuite, True)
    RunnerDummyTestCase.checkTestRun(testSuite, False)
    RunnerDummyTestCase.checkTearDownRun(testSuite, False)
    RunnerDummyTestCase.resetStates(testSuite)

    testSuite._manager.runSingleTestPartially(
        testSuite._testId, constants.RUN_TEST_NO_TEAR_DOWN
    )
    RunnerDummyTestCase.checkSetUpRun(testSuite, True)
    RunnerDummyTestCase.checkTestRun(testSuite, True)
    RunnerDummyTestCase.checkTearDownRun(testSuite, False)
    RunnerDummyTestCase.resetStates(testSuite)

    testSuite._manager.runSingleTestPartially(
        testSuite._testId, constants.RUN_TEST_FULL
    )
    RunnerDummyTestCase.checkSetUpRun(testSuite, True)
    RunnerDummyTestCase.checkTestRun(testSuite, True)
    RunnerDummyTestCase.checkTearDownRun(testSuite, True)


def checkLastRunInfo(testSuite):
    testSuite._manager.setStartDirOrModule(testSuite._modulePath)
    testSuite._manager.runTests(testSuite._testId)
    lastRunInfo = testSuite._manager.lastRunInfo()
    testSuite.assertTrue(lastRunInfo)
    testSuite.assertTrue(lastRunInfo.runTestIds[0].startswith(testSuite._testId))
    testSuite.assertEqual(lastRunInfo.failedTestId, None)
    testSuite.assertTrue(lastRunInfo.runCount)
    testSuite.assertTrue(lastRunInfo.successCount)
