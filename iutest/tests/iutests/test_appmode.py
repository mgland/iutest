import unittest

from iutest.qt import QtWidgets
from iutest import dcc


class AppModeTestCase(unittest.TestCase):
    @unittest.skipUnless(dcc.isInsideMaya(), "It is maya only test")
    def test_findParentMayaWindow(self):
        window = dcc.findParentWindow()
        self.assertTrue(window)
        self.assertTrue(isinstance(window, QtWidgets.QWidget))
        self.assertTrue("maya" in window.objectName().lower())

    @unittest.skipUnless(dcc.isStandalone(), "It is standalone only test")
    def test_findParentWindow(self):
        window = dcc.findParentWindow()
        self.assertFalse(window)
