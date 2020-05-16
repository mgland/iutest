import unittest
from utest.plugins import testlister
from utest import pathutils
from nose2.tools import params

class TestListerTestCase(unittest.TestCase):
    def test_listByDir(self):
        startDir = pathutils.utestPackageDir()
        topDir = pathutils.utestRootDir()
        tests = list(testlister.iterAllTestPathsFromRootDir(startDir, topDir))
        self.assertTrue(tests)
        print tests

    def test_listByModulePath(self):
        modulePath = 'utest.tests'
        tests = list(testlister.iterAllTestPathsFromRootDir(modulePath))
        self.assertTrue(tests)
        print tests

    @params(('package.to.module.testcase.test', False), 
            ('package.to.module.testcase.test:0', True))
    def test_parseParameterizedTestId(self, testId, expectParameterized):
        isParameterized, newTestId = testlister.parseParameterizedTestId(testId)
        self.assertEqual(isParameterized, expectParameterized)
        self.assertEqual(newTestId, testId.split(':')[0])
    
    # To-Do: test the support for the tests in egg file.
