from iutest.qt import QtCore, QtWidgets, Signal

class ScrollAreaPan(QtCore.QObject):
    """Enable a scrollable view to support MMB dragging to pan the view.
    """
    _MOUSE_EVENT_TYPES = (
        QtCore.QEvent.MouseButtonPress, 
        QtCore.QEvent.MouseMove,
        QtCore.QEvent.MouseButtonRelease
    )
    def __init__(self, scrollArea=None, hScrollBar=None, vScrollBar=None, scrollFactor=1.0):
        QtCore.QObject.__init__(self, scrollArea)
        self._scrollFactor = scrollFactor
        self._scrollArea = scrollArea
        if self._scrollArea:
            self._scrollArea.installEventFilter(self)

        self._hScrollBar = hScrollBar
        if not self._hScrollBar:
            self._hScrollBar = self._scrollArea.horizontalScrollBar() if self._scrollArea else None

        self._vScrollBar = vScrollBar
        if not self._vScrollBar:
            self._vScrollBar = self._scrollArea.verticalScrollBar() if self._scrollArea else None

        self._wasMMB = False
        self._startPressViewPnt = None
        self._currentPressViewPnt = None
        self._startHScrollValues = None
        self._startVScrollValues = None

    def _processContentMousePressEvent(self, event):
        self._wasMMB = bool(event.buttons() & QtCore.Qt.MidButton)
        if not self._wasMMB :
            return self._wasMMB 

        self._startPressViewPnt = self._currentPressViewPnt = event.globalPos()
        if self._hScrollBar:        
            self._startHScrollValues = self._hScrollBar.value()
        if self._vScrollBar:        
            self._startVScrollValues = self._vScrollBar.value()
        event.accept()
        return self._wasMMB

    def _processContentMouseMoveEvent(self, event):
        if not self._wasMMB:
            return self._wasMMB

        if self._startPressViewPnt is None:
            self._startPressViewPnt = self._currentPressViewPnt = event.globalPos()

        self._currentPressViewPnt = event.globalPos()
        gap = self._currentPressViewPnt - self._startPressViewPnt
        self._panViewBy(gap)
        event.accept()
        return self._wasMMB

    def _processContentMouseReleaseEvent(self, event):
        if not self._wasMMB:
            return False

        self._startPressViewPnt = None
        self._currentPressViewPnt = None
        event.accept()
        self._wasMMB = False
        return True

    def isMouseEvent(self, event):
        return event.type() in self._MOUSE_EVENT_TYPES

    def eventFilter(self, obj, event):
        if obj is not self._scrollArea:
            return False

        if not self.isMouseEvent(event):
            return False

        if event.type() == QtCore.QEvent.MouseButtonPress:
            return self._processContentMousePressEvent(event)

        if event.type() == QtCore.QEvent.MouseMove:
            return self._processContentMouseMoveEvent(event)

        return self._processContentMouseReleaseEvent(event)

    def _panViewBy(self, gap):
        if self._hScrollBar:
            self._hScrollBar.setValue(int(self._startHScrollValues - gap.x() * self._scrollFactor))
        if self._vScrollBar:
            self._vScrollBar.setValue(int(self._startVScrollValues - gap.y() * self._scrollFactor))