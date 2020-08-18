import argparse
import logging
import sys
import os

logger = logging.getLogger(__name__)


def runUi(modulePathOrDir=None, topDir=None, exit_=False):
    """Load the IUTest UI

    Args:
        modulePathOrDir (str): The directory or the module path to search for tests.
        topDir (str): The top directory that need to be put in sys.path in order for the tests work.
        exit (bool): Whether we exit python console after the IUTest window closed.
    """
    from iutest import qt as _qt
    if not _qt.checkQtAvailability():
        return

    from iutest.ui import iutestwindow
    with _qt.ApplicationContext(exit_=exit_) as ctx:
        if ctx.isStandalone:
            logging.basicConfig()
        try:
            manager = iutestwindow.IUTestWindow(
                startDirOrModule=modulePathOrDir, topDir=topDir
            )
            manager.show()
        except Exception:
            ctx.setHasError(True)
            logger.exception("Error loading IUTest window.")


def runTests(runnerName, *testModulePathsOrDir, **arguments):
    """Run the tests without UI

    Args:
        runnerName (str): The runner name, e.g. 'nose2' or 'pytest'
        testModulePathsOrDir (tuple): List of python module paths or a single directory contains test modules.
        miscArguments (dict): Typical supported arguments are:
            topDir (str): The dir contains the python modules that the tests need for running.
            stopOnError (bool): Stop the tests running on the first error/failure.
    """
    from iutest.core import testmanager
    from iutest.core.runners import runnerconstants
    dirs = [s for s in testModulePathsOrDir if os.path.isdir(s)]
    if len(dirs) > 1:
        logger.error("Please only input at most one test root dir once at a time.")
        return

    testRootDir =  dirs[0] if dirs else None
    topDir  = arguments.get("topDir", None)
    stopOnError = arguments.get("stopOnError", False)
    manager = testmanager.TestManager(ui=None, startDirOrModule=testRootDir, topDir=topDir)
    manager.setRunnerMode(runnerconstants.runnerModeFromName(runnerName))
    manager.setStopOnError(stopOnError)
    if testRootDir:
        manager.runAllTests()
    else:
        manager.runTests(*testModulePathsOrDir)


def main():
    from iutest import _version
    from iutest.core.runners import runnerconstants

    parser = argparse.ArgumentParser(description="IUTest")
    parser.add_argument(
        "-v", "--version", action="version", version=_version.__version__
    )

    parser.add_argument(
        "-u",
        "--ui",
        action="store_true",
        dest="ui",
        default=False,
        help="Run test interactively in IUTest UI",
    )

    parser.add_argument(
        "-e",
        "--stopOnError",
        action="store_true",
        dest="stopOnError",
        default=False,
        help="Stop test running once there is an test error or failure",
    )

    parser.add_argument(
        "-t",
        "--topDir",
        action="store",
        dest="topDir",
        help="Specify the top dir of the python module to import",
    )

    parser.add_argument(
        "-m",
        "--runner",
        action="store",
        dest="runner",
        help="The runner the runs the tests, e.g. 'nose2' or 'pytest'",
    )

    parser.add_argument(
        "-r",
        "--runTests",
        action="append",
        default=[],
        dest="testPathsOrDir",
        help="Specify the top dir of the python module to import",
    )

    # parse the arguments from standard input
    results = parser.parse_args()
    if len(sys.argv) < 2 or results.ui:
        testDir = results.testPathsOrDir[0] if results.testPathsOrDir else None
        runUi(testDir, topDir=results.topDir)
    else:
        if not results.testPathsOrDir:
            print(
                "You need to specify -r/--runTests with a directory or python module paths to run the tests."
            )
            return

        if not runnerconstants.isValidRunnerName(results.runner):
            print(
                "You need to specify a valid test runner, e.g. --runner 'nose2' or --runner 'pytest'"
            )
            return

        arguments = {
            "topDir" : results.topDir,
            "stopOnError" : results.stopOnError,
        }
        runTests(
            results.runner,
            *results.testPathsOrDir,
            **arguments
        )


if __name__ == "__main__":
    main()
