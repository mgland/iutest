import collections
import copy

from iutest.core import iconutils
from iutest.qt import QtCore, QtWidgets
from iutest.ui import uiutils

class InlineButtonLineEdit(QtWidgets.QLineEdit):
    _clearIcon = None
    
    _CLEAR_BUTTON_ID = "__clear__"
    _BUTTON_GAP = 2
    _BUTTON_DIMENTION = 20

    def __init__(self, withClearButton=False, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)
        self._buttons = collections.OrderedDict()
        self._initMargins = self.getTextMargins()
        self._initIcons()

        if withClearButton:
            self.addClearButton()
        
    @classmethod
    def _initIcons(cls):
        if cls._clearIcon:
            return

        iconutils.initSingleClassIcon(cls, "_clearIcon", "clear.svg")

    def addButton(self, btnId, button):
        existBtn = self._buttons.get(btnId)
        if existBtn:
            return existBtn

        button.setFixedSize(QtCore.QSize(self._BUTTON_DIMENTION, self._BUTTON_DIMENTION))
        button.setParent(self)
        button.setStyleSheet("background:transparent")
        self._buttons[btnId] = button
        self._refreshButtons()

    def addClearButton(self):
        existBtn = self.getClearButton()
        if existBtn:
            return existBtn

        btn = uiutils.makeIconButton(self._clearIcon, self)
        btn.setToolTip("Clear")
        btn.setVisible(False)
        btn.clicked.connect(self.clear)
        self.textChanged.connect(self._atTextChanged)
        self.addButton(self._CLEAR_BUTTON_ID, btn)

    def getClearButton(self):
        return self._buttons.get(self._CLEAR_BUTTON_ID)

    def setButtonEnabled(self, btnId, enabled):
        btn = self._buttons.get(btnId)
        if btn:
            btn.setEnabled(enabled)

    def setButtonVisible(self, btnId, visible):
        btn = self._buttons.get(btnId)
        if not btn or btn.isVisible() == visible:
            return

        btn.setVisible(visible)
        self._refreshButtons()

    def resizeEvent(self, event):
        QtWidgets.QLineEdit.resizeEvent(self, event)
        self._refreshButtons()

    def _atTextChanged(self, txt):
        if self.getClearButton():
            self.setButtonVisible(self._CLEAR_BUTTON_ID, bool(str(txt).strip()))

    def _refreshButtons(self):
        visibleButtons = [btn for btn in self._buttons.values() if btn.isVisible()]
        btnLen = len(visibleButtons)
        rightTxtMargin = btnLen * (self._BUTTON_DIMENTION + self._BUTTON_GAP)
        newTextMargin = list(copy.copy(self._initMargins))
        newTextMargin[2] = rightTxtMargin
        self.setTextMargins(*newTextMargin)
        w = self.width() - self.contentsMargins().right()
        halfH = self.height() / 2
        halfBtnH = self._BUTTON_DIMENTION / 2
        for i, btn in enumerate(visibleButtons):
            x = w - (i+1)*self._BUTTON_DIMENTION - i*self._BUTTON_GAP
            y = int(halfH - halfBtnH)
            btn.move(x, y)



    
