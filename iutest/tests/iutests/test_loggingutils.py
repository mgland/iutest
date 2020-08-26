# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

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
