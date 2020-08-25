import weakref
from iutest.qt import QtCore


class ScrollAreaPan(QtCore.QObject):
    """Enable a scrollable view to support MMB dragging to pan the view.
    """

    _MOUSE_EVENT_TYPES = (
        QtCore.QEvent.MouseButtonPress,
        QtCore.QEvent.MouseMove,
        QtCore.QEvent.MouseButtonRelease,
    )

    def __init__(
        self, scrollArea=None, hScrollBar=None, vScrollBar=None, scrollFactor=1.0
    ):
        QtCore.QObject.__init__(self, scrollArea)
        self._scrollFactor = scrollFactor
        self._scrollArea = weakref.ref(scrollArea)
        self._wasMMB = False
        self._startPressViewPnt = None
        self._currentPressViewPnt = None
        self._startHScrollValue = None
        self._startVScrollValue = None
        self._initStartScrollValues()

    def _scrollBars(self):
        if not self._scrollArea:
            return (None, None)

        return (
            self._scrollArea().horizontalScrollBar(),
            self._scrollArea().verticalScrollBar(),
        )

    def installEventFilterOn(self, widget):
        if widget:
            widget.installEventFilter(self)

    def _initStartScrollValues(self):
        hScrollBar, vScrollBar = self._scrollBars()
        if hScrollBar:
            self._startHScrollValue = hScrollBar.value()
        if vScrollBar:
            self._startVScrollValue = vScrollBar.value()

    def _processContentMousePressEvent(self, event):
        self._wasMMB = bool(event.buttons() & QtCore.Qt.MidButton)
        if not self._wasMMB:
            return self._wasMMB

        self._startPressViewPnt = self._currentPressViewPnt = event.globalPos()
        self._initStartScrollValues()
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
        if not self.isMouseEvent(event):
            return False

        if event.type() == QtCore.QEvent.MouseButtonPress:
            return self._processContentMousePressEvent(event)

        if event.type() == QtCore.QEvent.MouseMove:
            return self._processContentMouseMoveEvent(event)

        return self._processContentMouseReleaseEvent(event)

    def _panViewBy(self, gap):
        hScrollBar, vScrollBar = self._scrollBars()
        if hScrollBar:
            hScrollBar.setValue(
                int(self._startHScrollValue - gap.x() * self._scrollFactor)
            )
        if vScrollBar:
            vScrollBar.setValue(
                int(self._startVScrollValue - gap.y() * self._scrollFactor)
            )
