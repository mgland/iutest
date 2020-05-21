import unittest
import os

from utest.core import pathutils
from nose2.tools import params


class PathUtilsTestCase(unittest.TestCase):
    @params(
        ("/path/to/startDir", True),
        ("E:\\path\\to/startDir", True),
        ("module", False),
        ("package1.package2.module", False),
    )
    def test_isPath(self, input, expectedResult):
        self.assertEqual(pathutils.isPath(input), expectedResult)

    def test_utestRootDir(self):
        rootDir = pathutils.utestRootDir()
        self.assertTrue(os.path.isdir(rootDir))
        self.assertTrue("utest", os.listdir(rootDir))
        self.assertTrue(os.path.isfile(os.path.join(rootDir, "utest", "__init__.py")))

    def test_utestPackageDir(self):
        rootDir = pathutils.utestPackageDir()
        self.assertTrue(os.path.isdir(rootDir))
        self.assertTrue(os.path.isfile(os.path.join(rootDir, "__init__.py")))
