import unittest
import os

from iutest import dependencies

from iutest.plugins.nose2plugins import testlister
from iutest.core import pathutils

nose2 = dependencies.Nose2Wrapper.get()

class TestListerTestCase(unittest.TestCase):
    def test_listByDir(self):
        startDir = os.path.join(pathutils.iutestPackageDir(), "tests")
        topDir = pathutils.iutestRootDir()
        tests = list(testlister.iterAllTestPathsFromRootDir(startDir, topDir))
        self._checkListedTests(tests)

    def _checkListedTests(self, tests):
        self.assertTrue(tests)
        hasThisTest = False
        prefix = "iutest.tests.iutests.test_testlister.TestListerTestCase.test_"
        for tid in tests:
            if tid.startswith(prefix):
                hasThisTest = True
        self.assertTrue(hasThisTest)

    def test_listByModulePath(self):
        modulePath = "iutest.tests"
        tests = list(testlister.iterAllTestPathsFromRootDir(modulePath))
        self._checkListedTests(tests)

    @nose2.tools.params(
        ("package.to.module.testcase.test", False),
        ("package.to.module.testcase.test:0", True),
    )
    def test_parseParameterizedTestId(self, testId, expectParameterized):
        isParameterized, newTestId = testlister.parseParameterizedTestId(testId)
        self.assertEqual(isParameterized, expectParameterized)
        self.assertEqual(newTestId, testId.split(":")[0])

    # To-Do: test the support for the tests in egg file.
