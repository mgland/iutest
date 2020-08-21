import unittest
import os
import sys
import tempfile
import shutil

import iutest
from iutest import cli
from iutest.core import pathutils
from iutest.core.runners import runnerconstants

from iutest.tests.iutests import test_runnercommon as common


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self._tempModuleName = "test_iutest_cli_temp"
        self._tempDir = None
        self._runner = runnerconstants.RUNNER_NAMES[runnerconstants.RUNNER_PYUNIT]
        common.initTestTargets(self)

    def tearDown(self):
        if self._tempModuleName in sys.modules:
            del sys.modules[self._tempModuleName]
        
        if self._tempDir and os.path.isdir(self._tempDir):
            shutil.rmtree(self._tempDir)
            if self._tempDir in sys.path:
                sys.path.remove(self._tempDir)

    def _buildTempTests(self):
        if not self._tempDir or not os.path.isdir(self._tempDir):
            self._tempDir = tempfile.mkdtemp()

        # common.__file__ could be pyc file, what we need is py file:
        srcFile = os.path.join(os.path.dirname(common.__file__), "test_runnercommon.py")
        if not os.path.isfile(srcFile):
            return

        with open(srcFile, "r") as f:
            content = f.read()
            
        content = content.replace("RunnerDummyTestCase", "TempRunnerDummyTestCase")
        dstFile = os.path.join(self._tempDir, "{}.py".format(self._tempModuleName))
        with open(dstFile, "w") as f:
            f.write(content)
        self.assertTrue(os.path.isfile(dstFile))

        initFile = os.path.join(self._tempDir, "__init__.py")
        with open(initFile, "w"):
            pass
        self.assertTrue(os.path.isfile(initFile))

        if self._tempDir not in sys.path:
            sys.path.append(self._tempDir)

    def test_cliRunTestsByModulePath(self):
        runAction = lambda : cli.runTests(self._runner, self._testId)
        common.checkRunTestsAfterAction(self, runAction)

    def test_cliRunTestsByDirs(self):
        self._buildTempTests()
        import test_iutest_cli_temp as tempcommon
        runAction = lambda : cli.runTests(self._runner, self._tempDir)
        tempcommon.checkRunTestsAfterAction(self, runAction)

    def test_iutestRunTestsByModulePath(self):
        runAction = lambda : iutest.runTests(self._runner, self._testId)
        common.checkRunTestsAfterAction(self, runAction)

    def test_iurestRunTestsByDirs(self):
        self._buildTempTests()
        import test_iutest_cli_temp as tempcommon
        runAction = lambda : iutest.runTests(self._runner, self._tempDir)
        tempcommon.checkRunTestsAfterAction(self, runAction)
