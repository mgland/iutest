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
