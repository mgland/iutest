import logging
from utest.qt import QtCore
from utest.core import appsettings
from utest.core import constants

logger = logging.getLogger(__name__)

class CodeLineVisitor(QtCore.QObject):
    _editorSetting = None

    @classmethod
    def initEditorSetting(cls):
        cls._editorSetting = appsettings.get().simpleConfigValue(constants.CONFIG_KEY_CODE_EDITOR,
            constants.CONFIG_KEY_CODE_EDITOR_DEFAULT)

    @classmethod
    def config(cls):
        if not cls._editorSetting:
            cls.initEditorSetting()
        return cls._editorSetting

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self._process = QtCore.QProcess(self)

    def goTo(self, filePath, lineNumber=0):
        cmd = self.config()
        cmd = cmd.replace(constants.CODE_FILE_VAR, filePath)
        cmd = cmd.replace(constants.CODE_LINE_VAR, lineNumber)
        logger.debug(cmd)
        self._process.start(cmd)
