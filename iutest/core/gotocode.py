import logging
from iutest.core import appsettings
from iutest.core import constants
from iutest.qt import QtCore

logger = logging.getLogger(__name__)


class CodeLineVisitor(QtCore.QObject):
    _editorSetting = None

    @classmethod
    def initEditorSetting(cls):
        cls._editorSetting = appsettings.get().simpleConfigStrValue(
            constants.CONFIG_KEY_CODE_EDITOR, constants.CONFIG_KEY_CODE_EDITOR_DEFAULT
        )

    @classmethod
    def config(cls):
        if not cls._editorSetting:
            cls.initEditorSetting()
        return cls._editorSetting

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self._process = QtCore.QProcess(self)

    @staticmethod
    def _goToCmd(template, filePath, lineNumber):
        cmd = template.replace(constants.CODE_FILE_VAR, filePath)
        return cmd.replace(constants.CODE_LINE_VAR, str(lineNumber))

    def goTo(self, filePath, lineNumber=0):
        cmd = self._goToCmd(self.config(), filePath, lineNumber)
        logger.debug(cmd)
        self._process.start(cmd)
