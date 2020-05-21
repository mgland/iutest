import logging
import sys

logger = logging.getLogger(__name__)


class _QtModuleImporter(object):
    QtCore = None
    QtGui = None
    QtWidgets = None

    Signal = None

    @classmethod
    def _importFromPySide2(cls):
        try:
            from PySide2 import QtCore, QtGui, QtWidgets

            logger.debug("Using PySide2.")
            cls.QtCore = QtCore
            cls.QtGui = QtGui
            cls.QtWidgets = QtWidgets
            cls.Signal = QtCore.Signal
        except Exception:
            logger.debug("Unable to import PySide2.")

    @classmethod
    def _importFromPySide1(cls):
        try:
            from PySide import QtCore, QtGui

            logger.debug("Using PySide.")
            cls.QtCore = QtCore
            cls.QtGui = QtGui
            cls.QtWidgets = QtGui
            cls.Signal = QtCore.Signal
        except Exception:
            logger.debug("Unable to import PySide.")

    @classmethod
    def _importFromPyQt5(cls):
        try:
            from PyQt5 import QtCore, QtGui, QtWidgets

            logger.debug("Using PyQt5.")
            cls.QtCore = QtCore
            cls.QtGui = QtGui
            cls.QtWidgets = QtWidgets
            cls.Signal = QtCore.pyqtSignal
        except Exception:
            logger.debug("Unable to import PyQt5.")

    @classmethod
    def _importFromPyQt4(cls):
        try:
            from PyQt4 import QtCore, QtGui

            logger.debug("Using PyQt4.")
            cls._isPyQt = True
            cls.QtCore = QtCore
            cls.QtGui = QtGui
            cls.QtWidgets = QtGui
            cls.Signal = QtCore.pyqtSignal
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
Signal = _QtModuleImporter.Signal


def findTopLevelWidgetByName(name):
    for wgt in QtWidgets.QApplication.topLevelWidgets():
        if wgt.objectName() == name:
            return wgt
    return None


class ApplicationContext(object):
    """Enable widget works both in standalone mode or DCC embedded mode.
    """

    def __init__(self):
        self.isStandalone = False

    def __enter__(self):
        self._application = QtWidgets.QApplication.instance()
        self.isStandalone = False
        if not self._application:
            self._application = QtWidgets.QApplication(sys.argv)
            self.isStandalone = True
        return self

    def __exit__(self, *_, **__):
        if self.isStandalone:
            sys.exit(self._application.exec_())
