# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import unittest

from iutest.core.runners import runnerconstants
from iutest.core.runners import pyunitrunner
from iutest.tests.iutests import test_runnercommon as common


class PyUnitRunnerTestCase(unittest.TestCase):
    def setUp(self):
        common.setUpTest(self, runnerconstants.RUNNER_PYUNIT)

    def test_parseParameterizedTestId(self):
        common.checkParseParameterizedTestId(self)

    def test_isValid(self):
        self.assertTrue(pyunitrunner.PyUnitRunner.isValid())

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
