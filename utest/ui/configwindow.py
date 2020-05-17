import logging
import os

from utest.qt import QtCore, QtGui, QtWidgets
from utest.ui import uiutils

logger = logging.getLogger(__name__)


class ConfigWindow(QtWidgets.QWidget):
    """As there are not much to config and there won't be many in forseeable future, we use simple, 
    static way to generate these widgets.
    """
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._mainLayout = uiutils.makeMainLayout(self)
        self._formLayout = uiutils.makeMinorLayout(QtWidgets.QFormLayout)
        self._formLayout.setLabelAlignment(QtCore.Qt.AlignRight)

        # Code viewing config
        
        