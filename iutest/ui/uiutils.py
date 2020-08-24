from iutest.qt import QtCore, QtGui, QtWidgets


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


def makeMenuToolButton(icon=None, toolTip="", parent=None):
    btn = QtWidgets.QToolButton(parent)
    if icon:
        btn.setIcon(icon)
    btn.setToolTip(toolTip)
    btn.setContentsMargins(0, 0, 0, 0)
    btn.setIconSize(QtCore.QSize(20, 20))
    btn.setPopupMode(btn.InstantPopup)
    menu = QtWidgets.QMenu(btn)
    btn.setMenu(menu)
    return (btn, menu)


def addSeparatorToLayout(layout, direction):
    sep = QtWidgets.QFrame()
    sep.setStyleSheet("color:black")
    policy = sep.sizePolicy()
    if direction == QtCore.Qt.Horizontal:
        sep.setFrameShape(sep.HLine)
        sep.setSizePolicy(policy.Minimum, policy.Preferred)
    else:
        sep.setFrameShape(sep.VLine)
        sep.setSizePolicy(policy.Preferred, policy.Minimum)

    sep.setLineWidth(1)
    layout.addWidget(sep)


def popUpMessageOnCursorPos(msg, bgWidget=None):
    gpos = QtGui.QCursor.pos()
    QtWidgets.QWhatsThis.showText(gpos, msg, bgWidget)
