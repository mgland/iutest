from PySide2 import QtCore

from utest import constants


def createIniSettings(toolName):
    return QtCore.QSettings(
        QtCore.QSettings.IniFormat,
        QtCore.QSettings.UserScope,
        constants.ORG_MGLAND,
        toolName,
    )
