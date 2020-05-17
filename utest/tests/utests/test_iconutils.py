import unittest
import os

from utest.core import iconutils

class IconUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self._iconFile = 'testItem.svg'

    def test_iconPath(self):
        iconPath = iconutils.iconPath(self._iconFile)
        self.assertTrue(iconPath)
        self.assertTrue(os.path.isfile(iconPath))

    def test_iconPathSet(self):
        iconPaths = iconutils.iconPathSet(self._iconFile)
        self.assertTrue(iconPaths)
        for iconPath in iconPaths:
            self.assertTrue(iconPath)
            self.assertTrue(os.path.isfile(iconPath))
