import logging
from iutest import qt as _qt
from iutest import dependencies
from iutest.core import iconutils
from iutest.core import pathutils
from iutest.core.testrunners import base
from iutest.core.testrunners import runnerconstants

logger = logging.getLogger(__name__)


class Nose2TestRunner(base.BaseTestRunner):
    _Icon = None

    viewupdater = None
    testlister = None
    partialtest = None

    @classmethod
    def _importPlugins(cls):
        if cls.viewupdater and cls.testlister and cls.partialtest:
            return True

        try:
            from iutest.plugins.nose2plugins import viewupdater
            from iutest.plugins.nose2plugins import testlister
            from iutest.plugins.nose2plugins import partialtest

            cls.viewupdater = viewupdater
            cls.testlister = testlister
            cls.partialtest = partialtest
            return True
        except:
            cls.viewupdater = None
            cls.testlister = None
            cls.partialtest = None
            return False

    def isDummy(self):
        return False

    @classmethod
    def mode(cls):
        return runnerconstants.RUNNER_NOSE2

    @classmethod
    def isValid(cls):
        return dependencies.Nose2Wrapper.get().isValid()

    @classmethod
    def icon(cls):
        if not cls._Icon:
            cls._Icon = _qt.iconFromPath(iconutils.iconPath("nose2.svg"))
        return cls._Icon

    def runTests(self, *testIds):
        plugins = [
            "iutest.plugins.nose2plugins.uilogger",
            "nose2.plugins.loader.eggdiscovery",
            "iutest.plugins.nose2plugins.removeduplicated",
        ]
        excludePlugins = [
            "iutest.plugins.nose2plugins.testlister",
            "iutest.plugins.nose2plugins.partialtest",
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

        self.viewupdater.ViewUpdater.resetLastData()
        dependencies.Nose2Wrapper.getModule().discover(
            argv=argv,
            exit=False,
            extraHooks=self.viewupdater.ViewUpdater.getHooks(self._manager.ui()),
        )

    def runSingleTestPartially(self, testId, partialMode):
        """Run partial steps of test, like running setUp only, or setUp and test but without teardown.
        Args:
            testId (str): id of test, the python module.
            partialMode (int): the test run mode, available values are:
                constants.RUN_TEST_SETUP_ONLY | constants.RUN_TEST_NO_TEAR_DOWN
        """
        if not self._importPlugins():
            logger.warning(
                "Unable to import nose2 plugs to run tests, is nose2 installed?"
            )
            return

        plugins = [
            "iutest.plugins.nose2plugins.uilogger",
            "nose2.plugins.loader.eggdiscovery",
            "iutest.plugins.nose2plugins.removeduplicated",
            "iutest.plugins.nose2plugins.partialtest",
        ]
        excludePlugins = [
            "iutest.plugins.nose2plugins.testlister",
            "nose2.plugins.result",
        ]
        extraArgs = ["--partial-test"]
        self.partialtest.PartialTestRunner.setRunMode(partialMode)
        self._runTest(plugins, excludePlugins, extraArgs, testId)

    def iterAllTestIds(self):
        if not self._importPlugins():
            logger.warning(
                "Unable to import nose2 plugins to list out tests, is nose2 installed?"
            )
            return

        startDirOrModule = self._manager.startDirOrModule()
        topDir = self._manager.topDir()
        for tid in self.testlister.iterAllTestPathsFromRootDir(
            startDirOrModule, topDir
        ):
            yield tid

    @classmethod
    def lastListerError(cls):
        if not cls._importPlugins():
            return None

        return cls.testlister.gotErrorOnLastList()

    @classmethod
    def lastRunInfo(cls):
        info = base.TestRunInfo()
        if not cls._importPlugins():
            return info

        info.lastRunTestIds = cls.viewupdater.ViewUpdater.lastRunTestIds
        info.lastFailedTest = cls.viewupdater.ViewUpdater.lastFailedTest
        info.lastRunTime = cls.viewupdater.ViewUpdater.runTime
        info.lastRunCount = cls.viewupdater.ViewUpdater.lastRunCount
        info.lastSuccessCount = cls.viewupdater.ViewUpdater.lastSuccessCount
        info.lastFailedCount = cls.viewupdater.ViewUpdater.lastFailedCount
        info.lastErrorCount = cls.viewupdater.ViewUpdater.lastErrorCount
        info.lastSkipCount = cls.viewupdater.ViewUpdater.lastSkipCount
        info.lastExpectedFailureCount = (
            cls.viewupdater.ViewUpdater.lastExpectedFailureCount
        )
        info.lastUnexpectedSuccessCount = (
            cls.viewupdater.ViewUpdater.lastUnexpectedSuccessCount
        )
        return info

    @classmethod
    def parseParameterizedTestId(cls, testId):
        if not cls._importPlugins():
            return None

        return cls.testlister.parseParameterizedTestId(testId)

    @classmethod
    def sourcePathAndLineFromModulePath(cls, modulePath):
        if not cls._importPlugins():
            return None

        return cls.testlister.sourcePathAndLineFromModulePath(modulePath)
