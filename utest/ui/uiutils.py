from utest.qt import QtCore, QtGui, QtWidgets


def makeMainLayout(hostWidget=None):
    _lay = QtWidgets.QVBoxLayout(hostWidget)
    _lay.setContentsMargins(6, 6, 6, 6)
    _lay.setSpacing(3)
    return _lay


def makeMinorLayout(layoutClass):
    _layout = layoutClass()
    _layout.setSpacing(3)
    _layout.setContentsMargins(0, 0, 0, 0)
    return _layout


def makeMinorHorizontalLayout():
    return makeMinorLayout(QtWidgets.QHBoxLayout)


def makeMinorVerticalLayout():
    return makeMinorLayout(QtWidgets.QVBoxLayout)


def makeIconButton(icon, parent=None):
    btn = QtWidgets.QPushButton("", parent)
    btn.setIcon(icon)
    btn.setFlat(True)
    btn.setIconSize(QtCore.QSize(20, 20))
    btn.setFixedSize(QtCore.QSize(24, 24))
    return btn
