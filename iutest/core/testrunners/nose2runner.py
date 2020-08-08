import logging
from iutest import dependencies
from iutest.core.testrunners import base
from iutest.core import pathutils
from iutest.plugins.nose2plugins import viewupdater
from iutest.plugins.nose2plugins import testlister
from iutest.plugins.nose2plugins import partialtest

logger = logging.getLogger(__name__)

class Nose2TestRunner(base.BaseTestRunner):
    @classmethod
    def name(cls):
        return "nose2"

    def runTests(self, *testIds):
        plugins = [
            "iutest.plugins.nose2plugins.uilogger",
            "nose2.plugins.loader.eggdiscovery",
            "iutest.plugins.nose2plugins.removeduplicated",
        ]
        excludePlugins = [
            "iutest.plugins.nose2plugins.testlister", 
            "iutest.plugins.nose2plugins.partialtest"
        ]
        self._runTest(plugins, excludePlugins, [], *testIds)

    def _runTest(self, plugins, excludePlugins, extraArgs, *testIds):
        if not testIds:
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

        startDirOrModule = self._manager.startDirOrModule()
        topDir = self._manager.topDir()
        # Add start and top dir to avoid potential module name conflict:
        if pathutils.isPath(startDirOrModule):
            argv.extend(["-s", startDirOrModule, "-t", topDir])

        argv.extend(testIds)
        argv.extend(["--fail-fast"] if self._manager.stopOnError() else [])

        viewupdater.ViewUpdater.resetLastData()
        dependencies.Nose2Wrapper.get().discover(
            argv=argv, exit=False, extraHooks=viewupdater.ViewUpdater.getHooks(self._manager.ui())
        )

    def runSingleTestPartially(self, testId, partialMode):
        """Run partial steps of test, like running setUp only, or setUp and test but without teardown.
        Args:
            testId (str): id of test, the python module.
            partialMode (int): the test run mode, available values are:
                constants.RUN_TEST_SETUP_ONLY | constants.RUN_TEST_NO_TEAR_DOWN
        """
        plugins = [
            "iutest.plugins.nose2plugins.uilogger",
            "nose2.plugins.loader.eggdiscovery",
            "iutest.plugins.nose2plugins.removeduplicated",
            "iutest.plugins.nose2plugins.partialtest",
        ]
        excludePlugins = [
            "iutest.plugins.nose2plugins.testlister", 
            "nose2.plugins.result"
        ]
        extraArgs = ["--partial-test"]
        partialtest.PartialTestRunner.setRunMode(partialMode)
        self._runTest(plugins, excludePlugins, extraArgs, testId)

    def iterAllTestIds(self):
        startDirOrModule = self._manager.startDirOrModule()        
        topDir = self._manager.topDir()
        for tid in testlister.iterAllTestPathsFromRootDir(
            startDirOrModule, topDir
        ):
            yield tid

    @classmethod
    def lastListerError(cls):
        return testlister.gotErrorOnLastList()

    @classmethod
    def lastRunTestIds(cls):
        return viewupdater.ViewUpdater.lastRunTestIds
