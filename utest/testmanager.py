import logging

from utest.libs import nose2
from utest import pathutils
from utest.plugins import viewupdater
from utest.plugins import testlister

logger = logging.getLogger(__name__)


class TestManager(object):
    def __init__(self, ui, startDir, topDir=None):
        self._testStartDirOrModule = ""
        self._topDir = ""
        self._stopOnError = False
        self._beforeTestStartHook = None
        self.setStartDirOrModule(startDir)
        self.setTopDir(topDir)
        self._ui = ui

    def setStartDirOrModule(self, startDir):
        self._testStartDirOrModule = startDir or ""
        if self._testStartDirOrModule:
            if not self._topDir or not self._testStartDirOrModule.startswith(
                self._topDir
            ):
                self._topDir = self._testStartDirOrModule

    def startDirOrModule(self):
        return self._testStartDirOrModule

    def setTopDir(self, topDir):
        self._topDir = topDir or ""
        if self._topDir:
            if (
                not self._testStartDirOrModule
                or not self._testStartDirOrModule.startswith(self._topDir)
            ):
                self._testStartDirOrModule = self._topDir

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

    def setBeforeTestStartHook(self, func):
        self._beforeTestStartHook = func

    def runTests(self, *tests):
        if not tests:
            logger.warning("No test to run.")
            return

        argv = [
            "nose2",
            "-v",
            "--plugin",
            "utest.plugins.uilogger",
            "--plugin",
            "nose2.plugins.loader.eggdiscovery",
            "--exclude-plugin",
            "utest.plugins.testlister",
        ]

        # Add start and top dir to avoid potential module name conflict:
        if pathutils.isPath(self._testStartDirOrModule):
            argv.extend(["-s", self._testStartDirOrModule, "-t", self._topDir])

        argv.extend(tests)
        argv.extend(["--fail-fast"] if self._stopOnError else [])

        if self._beforeTestStartHook:
            self._beforeTestStartHook(tests)

        viewupdater.ViewUpdater.resetLastData()
        nose2.discover(
            argv=argv, exit=False, extraHooks=viewupdater.ViewUpdater.getHooks(self._ui)
        )

    def iterAllTestIds(self):
        for tid in testlister.iterAllTestPathsFromRootDir(
            self._testStartDirOrModule, self._topDir
        ):
            yield tid

    def runAllTests(self):
        tests = list(self.iterAllTestIds())
        if not tests:
            logger.warning("No tests found to run.")
            return

        self.runTests(*tests)
