import unittest
import os
from iutest import dependencies
from iutest.core import pathutils

nose2 = dependencies.Nose2Wrapper.get()

class PathUtilsTestCase(unittest.TestCase):
    @nose2.tools.params(
        ("/path/to/startDir", True),
        ("E:\\path\\to/startDir", True),
        ("module", False),
        ("package1.package2.module", False),
    )
    def test_isPath(self, input, expectedResult):
        self.assertEqual(pathutils.isPath(input), expectedResult)

    def test_iutestRootDir(self):
        rootDir = pathutils.iutestRootDir()
        self.assertTrue(os.path.isdir(rootDir))
        self.assertTrue("iutest", os.listdir(rootDir))
        self.assertTrue(os.path.isfile(os.path.join(rootDir, "iutest", "__init__.py")))

    def test_iutestPackageDir(self):
        rootDir = pathutils.iutestPackageDir()
        self.assertTrue(os.path.isdir(rootDir))
        self.assertTrue(os.path.isfile(os.path.join(rootDir, "__init__.py")))
