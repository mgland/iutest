import logging
import sys

logger = logging.getLogger(__name__)

def _importFromPySide2():
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
        logger.debug('Using PySide2.')
        return (QtCore, QtGui, QtWidgets)
    except Exception:
        logger.debug('Unable to import PySide2.')
    return (None, None, None)


def _importFromPySide1():
    try:
        from PySide import QtCore, QtGui
        logger.debug('Using PySide.')
        return (QtCore, QtGui, QtGui)
    except Exception:
        logger.debug('Unable to import PySide.')
    return (None, None, None)


def _importFromPyQt5():
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets
        logger.debug('Using PyQt5.')
        return (QtCore, QtGui, QtWidgets)
    except Exception:
        logger.debug('Unable to import PyQt5.')
    return (None, None, None)


def _importFromPyQt4():
    try:
        from PyQt4 import QtCore, QtGui
        logger.debug('Using PyQt4.')
        return (QtCore, QtGui, QtGui)
    except Exception:
        logger.debug('Unable to import PyQt4.')
    return (None, None, None)


def _importQtModules():
    importers = (_importFromPySide2, _importFromPySide1, _importFromPyQt5, _importFromPyQt4)
    for importer in importers:
        QtCore, QtGui, QtWidgets = importer()
        if QtCore:
            return (QtCore, QtGui, QtWidgets)
    
    logger.error('No Qt modules found.')
    return (None, None, None)
    
QtCore, QtGui, QtWidgets = _importQtModules()


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
