# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

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


def runTests(runnerName, *testModulePathsOrDir, **arguments):
    """Run the tests without UI

    Args:
        runnerName (str): The runner name, e.g. 'nose2' or 'pytest'
        testModulePathsOrDir (tuple): List of python module paths or a single directory contains test modules.
        miscArguments (dict): Typical supported arguments are:
            topDir (str): The dir contains the python modules that the tests need for running.
            stopOnError (bool): Stop the tests running on the first error/failure.
    """
    from iutest import cli

    cli.runTests(runnerName, *testModulePathsOrDir, **arguments)


__all__ = ["importutils", "runUi", "runTests"]
