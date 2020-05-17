import inspect
import os
import sys


def _initNose2():
    """Nose2 and its plugins need to be imported from nose2.
    """
    filePath = os.path.abspath(inspect.getfile(inspect.currentframe()))
    path = os.path.join(os.path.dirname(filePath), "libs")
    if path not in sys.path:
        sys.path.append(path)


_initNose2()

from utest.core import testmanager
from utest.core import reimportall
from utest.ui import utestwindow


def runUi(startDirOrModule=None, topDir=None):
    """Load the UTest UI

    Args:
        startDirOrModule (str): The directory or the module path to search for tests.
        topDir (str): The top directory that need to be put in sys.path in order for the tests work.
    """
    manager = utestwindow.UTestWindow(startDirOrModule=startDirOrModule, topDir=topDir)
    manager.show()


def runAllTests(startDirOrModule=None, topDir=None, stopOnError=False):
    """Run all the tests without UI

    Args:
        startDirOrModule (str): The directory or the module path to search for tests.
        topDir (str): The top directory that need to be put in sys.path in order for the tests work.
        stopOnError (bool): Stop the tests running on the first error/failure.
    """
    manager = testmanager.TestManager(None, startDirOrModule=startDirOrModule, topDir=topDir)
    manager.setStopOnError(stopOnError)
    manager.runAllTests()


def runTests(*tests):
    """Run the tests without UI

    Args:
        tests (tuple): The tests input in arbitrary number. Each of them is a python module path str.
    """
    manager = testmanager.TestManager(None, startDirOrModule=None)
    manager.runTests(*tests)


__all__ = [
    'reimportall',
    'runUi',
    'runAllTests',
    'runTests',
]