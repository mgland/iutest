import logging
from iutest import dependencies
from iutest.core import pathutils
from iutest.core import runinfo
from iutest.core.runners import base
from iutest.core.runners import runnerconstants
from iutest.plugins.nose2plugins import duplicationremoval # it has no nose2 import

logger = logging.getLogger(__name__)


class Nose2TestRunner(base.BaseTestRunner):
    uihooks = None
    testlister = None
    partialtest = None

    @classmethod
    def _importPlugins(cls):
        if cls.uihooks and cls.testlister and cls.partialtest:
            return True

        try:
            from iutest.plugins.nose2plugins import uihooks
            from iutest.plugins.nose2plugins import testlister
            from iutest.plugins.nose2plugins import partialtest

            cls.uihooks = uihooks
            cls.testlister = testlister
            cls.partialtest = partialtest
            return True
        except:
            cls.uihooks = None
            cls.testlister = None
            cls.partialtest = None
            return False

    @classmethod
    def mode(cls):
        return runnerconstants.RUNNER_NOSE2

    @classmethod
    def isValid(cls):
        return dependencies.Nose2Wrapper.get().isValid()

    @classmethod
    def iconFileName(cls):
        return "nose2.svg"

    def runTests(self, *testIds):
        if not self._importPlugins():
            self._issueNotInstalledError()
            return

        plugins = [
            "iutest.plugins.nose2plugins.uihooks",
            "nose2.plugins.loader.eggdiscovery",
        ]
        excludePlugins = [
            "iutest.plugins.nose2plugins.testlister",
            "iutest.plugins.nose2plugins.partialtest",
        ]
        extraHooks = duplicationremoval.TestsDuplicationRemovalHooks.getHooks()
        self._runTest(plugins, excludePlugins, [], extraHooks, *testIds)

    def _runTest(self, plugins, excludePlugins, extraArgs, extraHooks, *testIds):
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
        self.uihooks.UiHooksPlugin.resetLastData()
        dependencies.Nose2Wrapper.getModule().discover(
            argv=argv, 
            exit=False,
            extraHooks=extraHooks
        )

    def runSingleTestPartially(self, testId, partialMode):
        """Run partial steps of test, like running setUp only, or setUp and test but without teardown.
        Args:
            testId (str): id of test, the python module.
            partialMode (int): the test run mode, available values are:
                constants.RUN_TEST_SETUP_ONLY | constants.RUN_TEST_NO_TEAR_DOWN
        """
        if not self._importPlugins():
            self._issueNotInstalledError()
            return

        plugins = [
            "iutest.plugins.nose2plugins.uihooks",
            "nose2.plugins.loader.eggdiscovery",
            "iutest.plugins.nose2plugins.partialtest",
        ]
        excludePlugins = [
            "iutest.plugins.nose2plugins.testlister",
            "nose2.plugins.result",
        ]
        extraArgs = ["--partial-test"]
        extraHooks = duplicationremoval.TestsDuplicationRemovalHooks.getHooks()
        self.partialtest.PartialTestRunner.setRunMode(partialMode)
        self._runTest(plugins, excludePlugins, extraArgs, extraHooks, testId)

    def iterAllTestIds(self):
        if not self._importPlugins():
            self._issueNotInstalledError()
            return

        startDirOrModule = self._manager.startDirOrModule()
        topDir = self._manager.topDir()
        for tid in self.testlister.iterAllTestPathsFromRootDir(
            startDirOrModule, topDir
        ):
            yield tid

    @classmethod
    def hasLastListerError(cls):
        if not cls._importPlugins():
            return False

        return cls.testlister.TestCollector.gotError

    @classmethod
    def lastRunInfo(cls):
        if not cls._importPlugins():
            return runinfo.TestRunInfo()
        return cls.uihooks.UiHooksPlugin.lastRunInfo
