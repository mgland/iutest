from iutest.core import importutils


def runUi(modulePathOrDir=None, topDir=None, exit_=False):
    """Load the IUTest UI

    Args:
        modulePathOrDir (str): The directory or the module path to search for tests.
        topDir (str): The top directory that need to be put in sys.path in order for the tests work.
        exit (bool): Whether we exit python console after the IUTest window closed.
    """
    from iutest import cli
    cli.runUi(modulePathOrDir=modulePathOrDir, topDir=topDir, exit_=exit_)


def runTests(runnerName, topDir=None, stopOnError=False, *testModulePathsOrDir):
    """Run the tests without UI

    Args:
        runnerName (str): The runner name, e.g. 'nose2' or 'pytest'
        topDir (str): The dir contains the python modules that the tests need for running.
        stopOnError (bool): Stop the tests running on the first error/failure.
        testModulePathsOrDir (tuple): List of python module paths or a single directory contains test modules.
    """
    from iutest import cli
    cli.runTests(runnerName, topDir, stopOnError, *testModulePathsOrDir)


__all__ = ["importutils", "runUi", "runTests"]
