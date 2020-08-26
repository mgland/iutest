# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import unittest
import os

from iutest.core import iconutils
from iutest.core import constants


class IconUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self._iconFile = "testCase.svg"

    def test_iconPath(self):
        iconPath = iconutils.iconPath(self._iconFile)
        self.assertTrue(iconPath)
        self.assertTrue(os.path.isfile(iconPath))

    def test_iconPathSet(self):
        iconPaths = iconutils.iconPathSet(self._iconFile, constants.TEST_ICON_SUFFIXES)
        self.assertTrue(iconPaths)
        for iconPath in iconPaths:
            self.assertTrue(iconPath)
            self.assertTrue(os.path.isfile(iconPath))
