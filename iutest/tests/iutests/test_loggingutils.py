import unittest
import os
import logging

from iutest.core import loggingutils
from iutest.core import constants


class LoggingUtilsTestCase(unittest.TestCase):
    def test_loggingLevelEdit(self):
        modules = ["iutest.core", "iutest.core.loggingutils", "iutest.core.constants"]
        allLevels = loggingutils.allLoggingLevel()
        self.assertTrue(allLevels)
        for level in allLevels:
            expectedLevels = [level] * len(modules)
            loggingutils.setLoggingLevel(level, *modules)
            self.assertEqual(list(loggingutils.loggingLevels(*modules)), expectedLevels)
