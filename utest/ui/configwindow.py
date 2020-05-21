import logging
import os

from utest.qt import QtCore, QtGui, QtWidgets
from utest.ui import uiutils
from utest.core import constants
from utest.core import appsettings
from utest.core import gotocode

logger = logging.getLogger(__name__)


class ConfigWindow(QtWidgets.QDialog):
    """As there are not much to config and there won't be many in forseeable future, we use simple, 
    static way to generate these widgets.
    """

    _instance = None

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle("{} Settings".format(constants.APP_NAME))

        self._mainLayout = uiutils.makeMainLayout(self)
        self._formLayout = uiutils.makeMinorLayout(QtWidgets.QFormLayout)
        self._mainLayout.addLayout(self._formLayout)
        self._formLayout.setLabelAlignment(QtCore.Qt.AlignRight)

        # Code viewing config
        self._codeEditorLE = QtWidgets.QLineEdit(self)
        editorSetting = gotocode.CodeLineVisitor.config()
        self._codeEditorLE.setText(editorSetting)
        self._codeEditorLE.editingFinished.connect(self._onCodeEditorEditFinished)
        self._codeEditorLE.setPlaceholderText("Example: pargram $file -argToLine $line")
        self._codeEditorLE.setToolTip(
            "Input the command to jump to the code at the line. \n"
            "$file is the placeholder for file path, $line is the line number."
        )
        _annoText = QtWidgets.QLabel(
            "Default: {}".format(constants.CONFIG_KEY_CODE_EDITOR_DEFAULT)
        )
        _annoText.setEnabled(False)

        self._formLayout.addRow("Go To Code Line", self._codeEditorLE)
        self._formLayout.addRow("", _annoText)

        self.setMinimumWidth(400)
        self.setMinimumHeight(100)

        self.destroyed.connect(self._onDialogDeleted)

    def _onCodeEditorEditFinished(self):
        txt = self._codeEditorLE.text().strip()
        appsettings.get().saveSimpleConfig(constants.CONFIG_KEY_CODE_EDITOR, txt)
        gotocode.CodeLineVisitor.initEditorSetting()

    @classmethod
    def _onDialogDeleted(cls, *_):
        cls._instance = None

    @classmethod
    def show(cls, parent=None):
        if not cls._instance:
            cls._instance = cls(parent)
        else:
            cls._instance.setParent(parent)
        cls._instance.exec_()
