# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import logging
import os
from iutest.core import appsettings
from iutest.core import constants
from iutest.qt import QtCore, Signal

logger = logging.getLogger(__name__)


class CodeLineVisitor(QtCore.QObject):
    _editorSetting = None

    errorIssued = Signal(str)

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
        self._lastCmd = None
        self._process = QtCore.QProcess(self)
        self._process.error.connect(self._onGoToCodeError)
        self._process.readyReadStandardError.connect(self._onReadyReadStandardError)

    @staticmethod
    def _goToCmd(template, filePath, lineNumber):
        cmd = template.replace(constants.CODE_FILE_VAR, filePath)
        return cmd.replace(constants.CODE_LINE_VAR, str(lineNumber))

    def goTo(self, filePath, lineNumber=0):
        if not os.path.isfile(filePath):
            logger.warning("%s is not a valid file.", filePath)

        self._lastCmd = self._goToCmd(self.config(), filePath, lineNumber)
        logger.debug(self._lastCmd)
        self._process.start(self._lastCmd)

    def _onGoToCodeError(self, err):
        msg = "<font color=red><b>Error: </b></font>"
        if err == self._process.FailedToStart:
            msg = (
                msg
                + "Failed to launch the program as it was either missing or insufficient permissions.<br><br>"
            )
            msg = (
                msg
                + "You might need to change the goToCode setting in Preference Dialog, e.g.<br>Specify full path to the program, etc."
            )
        elif err == self._process.Crashed:
            msg = msg + "The program to browse the code has crashed."
        elif err == self._process.Timedout:
            msg = msg + "The last goToCodeProcess.waitFor...() function timed out."
        elif err == self._process.WriteError:
            msg = (
                msg
                + "An error occurred when attempting to write to the goToCode process."
            )
        elif err == self._process.ReadError:
            msg = (
                msg
                + "An error occurred when attempting to read to the goToCode process."
            )
        else:
            msg = msg + "An unknown error occurred when attempting to go to the code."

        msg = msg + "<hr><font color=red><b>Failed Command:</b></font><br>{}".format(
            self._lastCmd
        )
        self.errorIssued.emit(msg)

    def _onReadyReadStandardError(self):
        logger.error(self.readAllStandardError())
