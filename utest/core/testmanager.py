import logging

from utest.core import pathutils
from utest.core.testrunners import registry

logger = logging.getLogger(__name__)


class TestManager(object):
    def __init__(self, ui, startDirOrModule, topDir=None):
        self._startDirOrModule = ""
        self._topDir = ""
        self._stopOnError = False
        self._ui = ui
        self._runnerMode = registry.RUNNER_NOSE2
        self._runners = {}
        self.setStartDirOrModule(startDirOrModule)
        self.setTopDir(topDir)

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
        self.setStartDirOrModule(startDirOrModule)
        topDir = topDir or self._topDir
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

    def setRunnerMode(self, runnerMode):
        """Switch to different runner for listing or running the tests.
        Args:
            runnerMode (int): One of RUNNER_* int constant defined in registry.
        """
        self._initialRunner(runnerMode)
        self._runnerMode = runnerMode

    def ui(self):
        return self._ui

    def _initialRunner(self, runnerMode):
        if runnerMode in self._runners:
            return True

        if runnerMode not in registry.RUNNER_REGISTRY:
            logger.error("The runner mode %s is invalid.", runnerMode)
            return False

        runnerModulePath = registry.RUNNER_REGISTRY[runnerMode]
        runnerClass = pathutils.objectFromDotPath(runnerModulePath)
        self._runners[runnerMode] = runnerClass(self)
        return True

    def getRunner(self):
        if not self._initialRunner(self._runnerMode):
            logger.error("Unable initialise the runner of mode %s", self._runnerMode)
            return None

        return self._runners[self._runnerMode]

    def runTests(self, *tests):
        runner = self.getRunner()
        if runner:
            runner.runTests(*tests)

    def iterAllTestIds(self):
        runner = self.getRunner()
        if runner:
            for testId in runner.iterAllTestIds():
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
        runner = self.getRunner()
        if runner:
            runner.runSingleTestPartially(testId, partialMode)
