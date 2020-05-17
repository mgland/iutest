from utest.core import constants
from utest.qt import QtCore


def createIniSettings(toolName):
    return QtCore.QSettings(
        QtCore.QSettings.IniFormat,
        QtCore.QSettings.UserScope,
        constants.ORG_MGLAND,
        toolName,
    )
