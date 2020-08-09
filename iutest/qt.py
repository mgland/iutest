import logging
import sys

logger = logging.getLogger(__name__)


class _QtModuleImporter(object):
    QtCore = None
    QtGui = None
    QtWidgets = None
    QtSvg = None

    Variant = None
    Signal = None

    IsQt5 = False

    @classmethod
    def _importFromPySide2(cls):
        try:
            from PySide2 import QtCore, QtGui, QtWidgets, QtSvg

            logger.debug("Using PySide2.")
            cls.QtCore = QtCore
            cls.QtGui = QtGui
            cls.QtSvg = QtSvg
            cls.QtWidgets = QtWidgets
            cls.Signal = QtCore.Signal
            cls.IsQt5 = True
        except Exception:
            logger.debug("Unable to import PySide2.")

    @classmethod
    def _importFromPySide1(cls):
        try:
            from PySide import QtCore, QtGui, QtSvg

            logger.debug("Using PySide.")
            cls.QtCore = QtCore
            cls.QtGui = QtGui
            cls.QtWidgets = QtGui
            cls.QtSvg = QtSvg
            cls.Signal = QtCore.Signal
            cls.IsQt5 = False
        except Exception:
            logger.debug("Unable to import PySide.")

    @classmethod
    def _importFromPyQt5(cls):
        try:
            from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg

            logger.debug("Using PyQt5.")
            cls.QtCore = QtCore
            cls.QtGui = QtGui
            cls.QtWidgets = QtWidgets
            cls.QtSvg = QtSvg
            cls.Signal = QtCore.pyqtSignal
            cls.Variant = QtCore.QVariant
            cls.IsQt5 = True
        except Exception:
            logger.debug("Unable to import PyQt5.")

    @classmethod
    def _importFromPyQt4(cls):
        try:
            from PyQt4 import QtCore, QtGui, QtSvg

            logger.debug("Using PyQt4.")
            cls._isPyQt = True
            cls.QtCore = QtCore
            cls.QtGui = QtGui
            cls.QtWidgets = QtGui
            cls.QtSvg = QtSvg
            cls.Signal = QtCore.pyqtSignal
            cls.Variant = QtCore.QVariant
            cls.IsQt5 = False
        except Exception:
            logger.debug("Unable to import PyQt4.")

    @classmethod
    def importModules(cls):
        importers = (
            cls._importFromPySide2,
            cls._importFromPySide1,
            cls._importFromPyQt5,
            cls._importFromPyQt4,
        )
        for importer in importers:
            importer()
            if cls.QtCore:
                return

        logger.error("No Qt modules found.")


_QtModuleImporter.importModules()
QtCore = _QtModuleImporter.QtCore
QtGui = _QtModuleImporter.QtGui
QtWidgets = _QtModuleImporter.QtWidgets
QtSvg = _QtModuleImporter.QtSvg
Signal = _QtModuleImporter.Signal


def findTopLevelWidgetByName(name):
    for wgt in QtWidgets.QApplication.topLevelWidgets():
        if wgt.objectName() == name:
            return wgt
    return None


def variantToPyValue(value):
    if _QtModuleImporter.Variant and isinstance(value, _QtModuleImporter.Variant):
        return value.toPyObject()
    return value


def iconFromPath(filePath):
    if QtGui != QtWidgets:
        return QtGui.QIcon(filePath)

    renderer = QtSvg.QSvgRenderer(filePath)
    pixmap = QtGui.QPixmap(renderer.defaultSize())
    pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QtGui.QIcon(pixmap)


def hasQt():
    return bool(QtCore)


def isQt5():
    return _QtModuleImporter.IsQt5


def setDarkStyle():
    presetStyles = ()
    if hasattr(QtGui, "QStyleFactory"):
        presetStyles = QtGui.QStyleFactory.keys()
    else:
        presetStyles = QtWidgets.QStyleFactory.keys()

    if "Fusion" in presetStyles:
        QtWidgets.QApplication.setStyle("Fusion")
    elif "plastique" in presetStyles:
        QtWidgets.QApplication.setStyle("plastique")

    palette = QtGui.QPalette()
    palette.setColor(palette.Window, QtGui.QColor(68, 68, 68))
    palette.setColor(palette.WindowText, QtGui.QColor(200, 200, 200))
    palette.setColor(palette.Base, QtGui.QColor(46, 46, 46))
    palette.setColor(palette.AlternateBase, QtGui.QColor(43, 43, 43))
    palette.setColor(palette.ToolTipBase, QtGui.QColor(46, 46, 46))
    palette.setColor(palette.ToolTipText, QtCore.Qt.white)
    palette.setColor(palette.Text, QtGui.QColor(200, 200, 200))
    palette.setColor(palette.Disabled, palette.Text, QtGui.QColor(120, 120, 120))
    palette.setColor(palette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(palette.ButtonText, QtGui.QColor(238, 238, 238))
    palette.setColor(palette.Disabled, palette.ButtonText, QtGui.QColor(120, 120, 120))
    palette.setColor(palette.BrightText, QtGui.QColor(238, 238, 238))
    palette.setColor(palette.Link, QtGui.QColor(42, 130, 218))
    palette.setColor(palette.Highlight, QtGui.QColor(82, 133, 166))
    palette.setColor(palette.HighlightedText, QtGui.QColor(238, 238, 238))
    QtWidgets.QApplication.setPalette(palette)


class ApplicationContext(object):
    """Enable widget works both in standalone mode or DCC embedded mode.
    """

    def __init__(self, darkStyle=True, exit_=False):
        self.isStandalone = False
        self._exit = exit_
        self._darkStyle = darkStyle
        self._hadError = False

    def setHasError(self, hasError):
        self._hadError = hasError

    def __enter__(self):
        self._application = QtWidgets.QApplication.instance()
        if not self._application:
            self.isStandalone = True
            self._application = QtWidgets.QApplication(sys.argv)
            if self._darkStyle:
                setDarkStyle()
        else:
            self.isStandalone = (
                hasattr(self._application, "_eventLoopExited")
                and self._application._eventLoopExited
            )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._hadError:
            return

        if self.isStandalone:
            if self._exit:
                sys.exit(self._application.exec_())
            else:
                self._application.exec_()
                self._application._eventLoopExited = True
