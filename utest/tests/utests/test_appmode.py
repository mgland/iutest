import unittest

from utest.qt import QtWidgets
from utest import dcc

class AppModeTestCase(unittest.TestCase):

    @unittest.skipUnless(dcc.appmode.isInsideMaya())
    def test_findParentMayaWindow(self):
        window = dcc.findParentWindow()
        self.assertTrue(window)
        self.assertTrue(isinstance(window, QtWidgets.QWidget))
        self.assertTrue('maya' in window.objectName().lower())

    @unittest.skipUnless(dcc.appmode.isStandalone())
    def test_findParentWindow(self):
        window = dcc.findParentWindow()
        self.assertTrue(window is None)
