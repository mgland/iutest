from qt import QtWidgets, QtCore


def findMayaWindow():
    for wgt in QtWidgets.QApplication.topLevelWidgets():
        if wgt.objectName() == "MayaWindow":
            return wgt
