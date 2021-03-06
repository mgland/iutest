# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import logging

from iutest.core import pathutils
from iutest.core.runners import runnerconstants
from iutest.core.runners import registry

logger = logging.getLogger(__name__)


class TestManager(object):
    def __init__(self, ui, startDirOrModule, topDir=None):
        self._startDirOrModule = ""
        self._topDir = ""
        self._stopOnError = False
        self._ui = ui
        self._runnerMode = runnerconstants.RUNNER_PYUNIT
        self._runners = {}
        self.setStartDirOrModule(startDirOrModule)
        self.setTopDir(topDir)
        self._verbosity = 1

    def setVerbosity(self, verbosity):
        self._verbosity = verbosity

    def verbosity(self):
        return self._verbosity

    def setRunnerMode(self, runnerMode):
        """Switch to different runner for listing or running the tests.
        Args:
            runnerMode (int): One of RUNNER_* int constant defined in registry.
        """
        self._initialiseRunner(runnerMode)
        self._runnerMode = runnerMode
        self.getRunner().check()

    def iterAllRunners(self):
        for runnerMode in registry.getRunnerModes():
            runner = self.getRunnerByMode(runnerMode)
            if runner:
                yield runner

    def getFeasibleRunnerMode(self):
        for runnerMode in registry.getRunnerModes():
            runner = self.getRunnerByMode(runnerMode)
            if runner.isValid():
                return runnerMode

        return runnerconstants.RUNNER_PYUNIT

    def setStartDirOrModule(self, startDirOrModule):
        self._startDirOrModule = startDirOrModule or ""
        if self._startDirOrModule:
            if not self._topDir or not self._startDirOrModule.startswith(self._topDir):
                self._topDir = self._startDirOrModule

    def startDirOrModule(self):
        return self._startDirOrModule

    def setTopDir(self, topDir):
        self._topDir = topDir or ""
        if self._topDir:
            if not self._startDirOrModule or not self._startDirOrModule.startswith(
                self._topDir
            ):
                self._startDirOrModule = self._topDir

    def topDir(self):
        return self._topDir

    def setDirs(self, startDirOrModule, topDir=None):
        startDirOrModule = str(startDirOrModule) if startDirOrModule else ""
        self.setStartDirOrModule(startDirOrModule)
        topDir = topDir or self._topDir
        topDir = str(topDir) if topDir else ""
        if startDirOrModule:
            if topDir:
                if not self._topDir or not topDir.startswith(self._topDir):
                    self._topDir = topDir
            else:
                if not self._topDir or not startDirOrModule.startswith(self._topDir):
                    self._topDir = startDirOrModule

    def setStopOnError(self, stop):
        self._stopOnError = stop

    def stopOnError(self):
        return self._stopOnError

    def ui(self):
        return self._ui

    def _initialiseRunner(self, runnerMode):
        if runnerMode in self._runners:
            return True

        if runnerMode not in registry.RUNNER_REGISTRY:
            logger.error("The runner %s is invalid.", runnerMode)
            return False

        runnerModulePath = registry.RUNNER_REGISTRY[runnerMode]
        runnerClass = pathutils.objectFromDotPath(runnerModulePath)
        self._runners[runnerMode] = runnerClass(self)
        return True

    def getRunnerByMode(self, runnerMode):
        if not self._initialiseRunner(runnerMode):
            logger.error("Unable to initialise the runner of mode %s", runnerMode)
            return None

        return self._runners[runnerMode]

    def getRunner(self):
        return self.getRunnerByMode(self._runnerMode)

    def runTests(self, *tests):
        self.getRunner().runTests(*tests)

    def iterAllTestIds(self):
        for testId in self.getRunner().iterAllTestIds():
            yield testId

    def runAllTests(self):
        tests = list(self.iterAllTestIds())
        if not tests:
            logger.warning("No tests found to run.")
            return

        self.runTests(*tests)

    def runSingleTestPartially(self, testId, partialMode):
        """Run partial steps of test, like running setUp only, or setUp and test but without teardown.
        Args:
            testId (str): id of test, the python module.
            partialMode (int): the test run mode, available values are:
                constants.RUN_TEST_SETUP_ONLY | constants.RUN_TEST_NO_TEAR_DOWN
        """
        self.getRunner().runSingleTestPartially(testId, partialMode)

    def hasLastListerError(self):
        return self.getRunner().hasLastListerError()

    def lastRunTestIds(self):
        return self.getRunner().lastRunTestIds()

    def lastRunInfo(self):
        return self.getRunner().lastRunInfo()

    def parseParameterizedTestId(self, testId):
        return self.getRunner().parseParameterizedTestId(testId)

    def lastFailedTestId(self):
        return self.getRunner().lastFailedTestId()

    def avoidRunTestsOnPackageLevel(self):
        return self.getRunner().avoidRunTestsOnPackageLevel()
