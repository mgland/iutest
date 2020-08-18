import unittest
import os
import sys
import tempfile
import shutil

from iutest.core import importutils
from iutest import dependencies

@unittest.skipUnless(importutils.isReimportFeatureAvailable(silentCheck=True), "reimport feature is unavailable.")
class ImportUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self._tempDir = tempfile.mkdtemp()
        self._varName = "myVariable"
        self._modFileName = "_testReimportModule"
        if self._tempDir not in sys.path:
            sys.path.append(self._tempDir)

    def _testModFilePath(self):
        return os.path.join(self._tempDir, (self._modFileName+".py"))

    def _writeModule(self, value):
        value = "'{}'".format(value) if isinstance(value, str) else value
        content = "{} = {}".format(self._varName, value)
        with open(self._testModFilePath(), "w") as f:
            f.write(content)

    def tearDown(self):
        mod = __import__(self._modFileName)
        del mod
        if self._modFileName in sys.modules:
            del sys.modules[self._modFileName]

        if os.path.isdir(self._tempDir):
            shutil.rmtree(self._tempDir)

        if self._tempDir in sys.path:
            sys.path.remove(self._tempDir)

    def _getVarValue(self):
        mod = __import__(self._modFileName)
        return getattr(mod, self._varName)

    def test_reimportByModulePath(self):
        action = lambda:importutils.reimportByModulePath(self._modFileName)
        self._checkReimport(action)

    def _checkReimport(self, reimportAction):
        oldValue = 1234
        self._writeModule(oldValue)
        self.assertEqual(self._getVarValue(), oldValue)

        values = [0, "abc", True]
        for v in values:
            self._writeModule(v)
            self.assertEqual(self._getVarValue(), oldValue)
            reimportAction()
            self.assertEqual(self._getVarValue(), v)
            oldValue = v

    def test_reimportAllChangedPythonModules(self):
        action = lambda:importutils.reimportAllChangedPythonModules(inclusiveKeyword=self._modFileName)
        self._checkReimport(action)
