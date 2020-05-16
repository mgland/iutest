import inspect
import os
import sys


def _initNose():
    """Nose2 and its plugins need to be import from nose2.
    """
    filePath = os.path.abspath(inspect.getfile(inspect.currentframe()))
    path = os.path.join(os.path.dirname(filePath), "libs")
    if path not in sys.path:
        sys.path.append(path)


_initNose()

from utest import utestwindow
from utest import testmanager


def runUi(startDirOrModule=None, topDir=None):
    """Load the UTest UI
    """
    manager = utestwindow.UTestWindow(startDirOrModule=startDirOrModule, topDir=topDir)
    manager.show()


def runAllTests(startDirOrModule=None, topDir=None, failEarly=False):
    manager = testmanager.TestManager(None, startDir=startDirOrModule, topDir=topDir)
    manager.setStopOnError(failEarly)
    manager.runAllTests()


def runTests(*tests):
    manager = testmanager.TestManager(None, startDir=None)
    manager.runTests(*tests)
