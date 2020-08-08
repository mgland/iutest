import inspect
import os
import sys
import logging

from iutest import qt as _qt
from iutest.core import testmanager
from iutest.core import importutils
from iutest.ui import iutestwindow

logger = logging.getLogger(__name__)

def runUi(startDirOrModule=None, topDir=None, exit_=False):
    """Load the IUTest UI

    Args:
        startDirOrModule (str): The directory or the module path to search for tests.
        topDir (str): The top directory that need to be put in sys.path in order for the tests work.
        exit (bool): Whether we exit python console after the IUTest window closed.
    """
    with _qt.ApplicationContext(exit_=exit_) as ctx:
        if ctx.isStandalone:
            logging.basicConfig()
        try:
            manager = iutestwindow.IUTestWindow(
                startDirOrModule=startDirOrModule, topDir=topDir
            )
            manager.show()
        except Exception:
            ctx.setHasError(True)
            logger.exception("Error loading IUTest window.")


def runAllTests(startDirOrModule=None, topDir=None, stopOnError=False):
    """Run all the tests without UI

    Args:
        startDirOrModule (str): The directory or the module path to search for tests.
        topDir (str): The top directory that need to be put in sys.path in order for the tests work.
        stopOnError (bool): Stop the tests running on the first error/failure.
    """
    manager = testmanager.TestManager(
        None, startDirOrModule=startDirOrModule, topDir=topDir
    )
    manager.setStopOnError(stopOnError)
    manager.runAllTests()


def runTests(*tests):
    """Run the tests without UI

    Args:
        tests (tuple): The tests input in arbitrary number. Each of them is a python module path str.
    """
    manager = testmanager.TestManager(None, startDirOrModule=None)
    manager.runTests(*tests)


__all__ = ["importutils", "runUi", "runAllTests", "runTests"]
