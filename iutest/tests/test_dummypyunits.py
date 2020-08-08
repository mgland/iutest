import unittest
import logging

from iutest import dependencies
from iutest.core import constants

logger = logging.Logger(__name__)
nose2 = dependencies.Nose2Wrapper.get()


class DummyTests(unittest.TestCase):
    """Some dummy tests for the IUTest UI manual tests.
    """

    def setUp(self):
        print("Call {}.setUp()".format(self.__class__.__name__))

    def tearDown(self):
        print("Call {}.tearDown()".format(self.__class__.__name__))

    def test_passed(self):
        logger.info("About to pass.")
        self.assertTrue(True)

    @unittest.skip("Test the skipped tests.")
    def test_skipped(self):
        pass

    def test_error(self):
        logger.warning("About to have test error.")
        raise RuntimeError("A test error.")

    def test_failed(self):
        self.assertTrue(False, "False will never be True.")

    @unittest.expectedFailure
    def test_expectedFailureButSuccess(self):
        logger.warning("This should not pass.")
        self.assertTrue(True)

    @unittest.expectedFailure
    def test_expectedFailure(self):
        logger.warning("This should not pass.")
        self.assertTrue(False)

    @unittest.skipUnless(
        hasattr(unittest.TestCase, "subTest"),
        "Current TestCase version does not support subTest",
    )
    def test_subTests(self):
        for i in range(0, 6):
            with self.subTest(i=i):
                self.assertEqual(i % 2, 0)

    @nose2.tools.params((1, 2), (2, 3), (6, 5), (4, 6))
    def test_parameters(self, num1, num2):
        logger.info("Test with %s < %s", num1, num2)
        self.assertLess(num1, num2)
