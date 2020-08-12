import unittest
import os
from iutest.core import pathutils


class PathUtilsTestCase(unittest.TestCase):
    def test_isPath(self):
        data = (
            ("/path/to/startDir", True),
            ("E:\\path\\to/startDir", True),
            ("module", False),
            ("package1.package2.module", False),
        )
        for _input, expectedResult in data:
            self.assertEqual(pathutils.isPath(_input), expectedResult)

    def test_iutestRootDir(self):
        rootDir = pathutils.iutestRootDir()
        self.assertTrue(os.path.isdir(rootDir))
        self.assertTrue("iutest", os.listdir(rootDir))
        self.assertTrue(os.path.isfile(os.path.join(rootDir, "iutest", "__init__.py")))

    def test_iutestPackageDir(self):
        rootDir = pathutils.iutestPackageDir()
        self.assertTrue(os.path.isdir(rootDir))
        self.assertTrue(os.path.isfile(os.path.join(rootDir, "__init__.py")))

    def test_objectFromDotPath(self):
        from iutest import core as corePackage
        from iutest.core import testmanager as testmanagerMod
        data = {
            "iutest.core":corePackage,
            "iutest.core.testmanager":testmanagerMod,
            "iutest.core.testmanager.TestManager":testmanagerMod.TestManager,
            "iutest.core.testmanager.TestManager.setRunnerMode":testmanagerMod.TestManager.setRunnerMode,
            "iutest.core.testmanager.logger":testmanagerMod.logger,
        }
        for dotPath, expectedObj in data.items():
            self.assertEqual(pathutils.objectFromDotPath(dotPath), expectedObj)

    def test_sourceFileAndLineFromObject(self):
        from iutest import core as corePackage
        from iutest.core import testmanager as testmanagerMod
        data = [
            (corePackage, False),
            (testmanagerMod, False),
            (testmanagerMod.TestManager, True), 
            (testmanagerMod.TestManager.setRunnerMode, True),
        ]
        for obj, notLine0 in data:
            srcFile, line = pathutils.sourceFileAndLineFromObject(obj)
            self.assertTrue(srcFile)
            self.assertTrue(os.path.isfile(srcFile))
            self.assertEqual(bool(line), notLine0)
