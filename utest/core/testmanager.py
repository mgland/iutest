import logging

from utest.libs import nose2
from utest.core import pathutils
from utest.plugins import viewupdater
from utest.plugins import testlister
from utest.plugins import partialtest

logger = logging.getLogger(__name__)


class TestManager(object):
    def __init__(self, ui, startDirOrModule, topDir=None):
        self._startDirOrModule = ""
        self._topDir = ""
        self._stopOnError = False
        self.setStartDirOrModule(startDirOrModule)
        self.setTopDir(topDir)
        self._ui = ui

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

    def _runTest(self, plugins, excludePlugins, extraArgs, *tests):
        if not tests:
            logger.warning("No test to run.")
            return

        argv = ["nose2", "-v"]
        for plugin in plugins:
            argv.append("--plugin")
            argv.append(plugin)

        for plugin in excludePlugins:
            argv.append("--exclude-plugin")
            argv.append(plugin)

        argv.extend(extraArgs)

        # Add start and top dir to avoid potential module name conflict:
        if pathutils.isPath(self._startDirOrModule):
            argv.extend(["-s", self._startDirOrModule, "-t", self._topDir])

        argv.extend(tests)
        argv.extend(["--fail-fast"] if self._stopOnError else [])

        viewupdater.ViewUpdater.resetLastData()
        nose2.discover(
            argv=argv, exit=False, extraHooks=viewupdater.ViewUpdater.getHooks(self._ui)
        )

    def runTests(self, *tests):
        plugins = [
            "utest.plugins.uilogger",
            "nose2.plugins.loader.eggdiscovery",
            "utest.plugins.removeduplicated",
        ]
        excludePlugins = ["utest.plugins.testlister", "utest.plugins.partialtest"]
        self._runTest(plugins, excludePlugins, [], *tests)

    def iterAllTestIds(self):
        for tid in testlister.iterAllTestPathsFromRootDir(
            self._startDirOrModule, self._topDir
        ):
            yield tid

    def runAllTests(self):
        tests = list(self.iterAllTestIds())
        if not tests:
            logger.warning("No tests found to run.")
            return

        self.runTests(*tests)

    def runTestPartial(self, testId, partialMode):
        """Run partial steps of test, like running setUp only, or setUp and test but without teardown.
        Args:
            testId (str): id of test, the python module.
            partialMode (int): the test run mode, available values are:
                constants.RUN_TEST_SETUP_ONLY | constants.RUN_TEST_NO_TEAR_DOWN
        """
        plugins = [
            "utest.plugins.uilogger",
            "nose2.plugins.loader.eggdiscovery",
            "utest.plugins.removeduplicated",
            "utest.plugins.partialtest",
        ]
        excludePlugins = ["utest.plugins.testlister", "nose2.plugins.result"]
        extraArgs = ["--partial-test"]
        partialtest.PartialTestRunner.setRunMode(partialMode)
        self._runTest(plugins, excludePlugins, extraArgs, testId)
