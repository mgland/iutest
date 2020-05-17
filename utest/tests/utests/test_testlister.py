import unittest
from utest.plugins import testlister
from utest import pathutils
from nose2.tools import params

class TestListerTestCase(unittest.TestCase):
    def test_listByDir(self):
        startDir = pathutils.utestPackageDir()
        topDir = pathutils.utestRootDir()
        tests = list(testlister.iterAllTestPathsFromRootDir(startDir, topDir))
        self._checkListedTests(tests)
    
    def _checkListedTests(self, tests):
        self.assertTrue(tests)
        hasThisTest = False
        prefix = 'utest.tests.utests.test_testlister.TestListerTestCase.test_'
        for tid in tests:
            if tid.startswith(prefix):
                hasThisTest = True
        self.assertTrue(hasThisTest)

    def test_listByModulePath(self):
        modulePath = 'utest.tests'
        tests = list(testlister.iterAllTestPathsFromRootDir(modulePath))
        self._checkListedTests(tests)

    @params(('package.to.module.testcase.test', False), 
            ('package.to.module.testcase.test:0', True))
    def test_parseParameterizedTestId(self, testId, expectParameterized):
        isParameterized, newTestId = testlister.parseParameterizedTestId(testId)
        self.assertEqual(isParameterized, expectParameterized)
        self.assertEqual(newTestId, testId.split(':')[0])
    
    # To-Do: test the support for the tests in egg file.
