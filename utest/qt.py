import logging

logger = logging.getLogger(__name__)

def _importFromPySide2():
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
        return (QtCore, QtGui, QtWidgets)
    except Exception:
        logger.debug('Unable to import PySide2.')
    return (None, None, None)


def _importFromPySide1():
    try:
        from PySide import QtCore, QtGui
        return (QtCore, QtGui, QtGui)
    except Exception:
        logger.debug('Unable to import PySide.')
    return (None, None, None)


def _importFromPyQt5():
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets
        return (QtCore, QtGui, QtWidgets)
    except Exception:
        logger.debug('Unable to import PyQt5.')
    return (None, None, None)


def _importFromPyQt4():
    try:
        from PyQt4 import QtCore, QtGui
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