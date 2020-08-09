import argparse
import logging

logger = logging.getLogger(__name__)

def runUi(startDirOrModule=None, topDir=None, exit_=False):
    """Load the IUTest UI

    Args:
        startDirOrModule (str): The directory or the module path to search for tests.
        topDir (str): The top directory that need to be put in sys.path in order for the tests work.
        exit (bool): Whether we exit python console after the IUTest window closed.
    """
    from iutest import qt as _qt
    from iutest.ui import iutestwindow
    if not _qt.hasQt():
        cmd = "`pip install PySide2`" 
        logger.error("Unable to launch IUTest UI which requires either PySide or PyQt installed, please: %s", cmd)
        return

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


def runAllTests(runnerName, startDirOrModule=None, topDir=None, stopOnError=False):
    """Run all the tests without UI

    Args:
        runnerName (str): The runner mode name, e.g. 'nose2' or 'pytest'
        startDirOrModule (str): The directory or the module path to search for tests.
        topDir (str): The top directory that need to be put in sys.path in order for the tests work.
        stopOnError (bool): Stop the tests running on the first error/failure.
    """
    from iutest.core import testmanager
    from iutest.core.testrunners import runnerconstants
    manager = testmanager.TestManager(
        None, startDirOrModule=startDirOrModule, topDir=topDir
    )
    manager.setRunnerMode(runnerconstants.runnerModeFromName(runnerName))
    manager.setStopOnError(stopOnError)
    manager.runAllTests()


def runTests(runnerName, *tests):
    """Run the tests without UI

    Args:
        tests (tuple): The tests input in arbitrary number. Each of them is a python module path str.
    """
    from iutest.core import testmanager
    from iutest.core.testrunners import runnerconstants
    manager = testmanager.TestManager(None, startDirOrModule=None)
    manager.setRunnerMode(runnerconstants.runnerModeFromName(runnerName))
    manager.runTests(*tests)


def main():
    from iutest import _version
    from iutest.core.testrunners import runnerconstants
    parser = argparse.ArgumentParser(description = "IUTest")
    parser.add_argument(
        "-v",
        "--version", 
        action = 'version',
        version = _version.__version__
    ) 

    parser.add_argument(
        "-u",
        "--ui",
        action='store_true', 
        dest='ui',
        default=False,
        help = "Run test interactively in IUTest UI"
    )

    parser.add_argument(
        "-e",
        "--stopOnError",
        action='store_true', 
        dest='stopOnError',
        default=False,
        help = "Stop test running once there is an test error or failure"
    )
    parser.add_argument(
        "-m",
        "--runner",
        action='store', 
        dest='runner',
        help = "The runner the runs the tests, e.g. 'nose2' or 'pytest'"
    )

    parser.add_argument(
        "-a",
        "--runAllTests",
        action='store', 
        dest='testRootDirOrModule',
        help = "Run all tests under the specified dir or python module"
    )

    parser.add_argument(
        "-t",
        "--topDir",
        action='store', 
        dest='topDir',
        help = "Specify the top dir of the python module to import"
    )

    parser.add_argument(
        "-r",
        "--runTest",
        action='append', 
        default=[],
        dest='testModulePaths',
        help = "Specify the top dir of the python module to import"
    )

	# parse the arguments from standard input 
    results = parser.parse_args()
    if not results.ui:
        if not runnerconstants.isValidRunnerName(results.runner):
            print("You need to specify a valid test runner, e.g. 'nose2' or 'pytest'")
            return

        if results.testRootDirOrModule:
            runAllTests(results.runner, results.testRootDirOrModule, topDir=results.topDir, stopOnError=results.stopOnError)
        if results.testModulePaths:
            runTests(results.runner, *results.testModulePaths)
    else:
        runUi(results.testRootDirOrModule, topDir=results.topDir)


if __name__ == "__main__":
    main()