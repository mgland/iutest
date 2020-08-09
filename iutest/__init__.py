from iutest.core import importutils

def runUi(startDirOrModule=None, topDir=None, exit_=False):
    """Load the IUTest UI

    Args:
        startDirOrModule (str): The directory or the module path to search for tests.
        topDir (str): The top directory that need to be put in sys.path in order for the tests work.
        exit (bool): Whether we exit python console after the IUTest window closed.
    """
    from iutest import cli
    cli.runUi(startDirOrModule=startDirOrModule, topDir=topDir, exit_=exit_)


def runAllTests(startDirOrModule=None, topDir=None, stopOnError=False):
    """Run all the tests without UI

    Args:
        startDirOrModule (str): The directory or the module path to search for tests.
        topDir (str): The top directory that need to be put in sys.path in order for the tests work.
        stopOnError (bool): Stop the tests running on the first error/failure.
    """
    from iutest import cli
    cli.runAllTests(startDirOrModule=startDirOrModule, topDir=topDir, stopOnError=stopOnError)


def runTests(*tests):
    """Run the tests without UI

    Args:
        tests (tuple): The tests input in arbitrary number. Each of them is a python module path str.
    """
    from iutest import cli
    cli.runTests(*tests)


__all__ = ["importutils", "runUi", "runAllTests", "runTests"]
