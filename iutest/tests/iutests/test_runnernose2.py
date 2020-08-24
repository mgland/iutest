import unittest
from iutest.tests.iutests import test_runnercommon as common
from iutest import dependencies
from iutest.core import pathutils
from iutest.core import pyunitutils
from iutest.core.runners import runnerconstants


@unittest.skipUnless(dependencies.Nose2Wrapper.get().isValid(), "It is nose2 only test")
class Nose2RunnerTestCase(unittest.TestCase):
    def setUp(self):
        common.setUpTest(self, runnerconstants.RUNNER_NOSE2)

    def test_parseParameterizedTestId(self):
        common.checkParseParameterizedTestId(self)

    def test_listByDir(self):
        common.checkListByDir(self)

    def test_listByModulePath(self):
        common.checkListByModulePath(self)

    def test_runTests(self):
        common.checkRunTests(self)

    def test_partialRun(self):
        common.checkPartialRun(self)

    def test_lastRunInfo(self):
        common.checkLastRunInfo(self)

    def test_testNotDuplicated(self):
        common.checkTestsNotDuplicated(self)
