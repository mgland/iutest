import unittest
import logging
import inspect
import nose2
from iutest.core import pathutils
from iutest.core import pyunitutils

logger = logging.getLogger(__name__)

def gotErrorOnLastList():
    return TestCollector.gotError


def iterAllTestPathsFromRootDir(startDirOrModuleName, topDir=None):
    argv = [
        "nose2",
        "--plugin",
        "iutest.plugins.nose2plugins.testlister",
        "--list-tests",
        "--plugin",
        "nose2.plugins.loader.eggdiscovery",
        "--plugin",
        "iutest.plugins.nose2plugins.removeduplicated",
        "--exclude-plugin",
        "nose2.plugins.result",
    ]
    if pathutils.isPath(startDirOrModuleName):
        argv.extend(["-s", startDirOrModuleName, "-t", topDir])
    else:
        argv.append(startDirOrModuleName)

    TestCollector.gotError = False
    nose2.discover(argv=argv, exit=False)
    for tid in TestCollector.iterTestIds():
        yield tid


class TestCollector(nose2.events.Plugin):
    """A nose2 plug to collect the tests without running them.
    """

    gotError = False
    commandLineSwitch = (None, "list-tests", "List test but not running them.")
    _mpmode = False
    _importFailureModule = "ModuleImportFailure"
    _loadTestsFailure = "LoadTestsFailure"
    _errorSeparator = "-" * 80

    _testIds = []

    def registerInSubprocess(self, event):
        event.pluginClasses.append(self.__class__)
        self._mpmode = True

    @classmethod
    def resetIds(cls):
        cls._testIds = []

    @classmethod
    def collectId(cls, testId):
        if testId not in cls._testIds:
            cls._testIds.append(testId)

    @classmethod
    def iterTestIds(cls):
        for tid in cls._testIds:
            yield tid

    def startTestRun(self, event):
        self.resetIds()
        if self._mpmode:
            return
        event.executeTests = self.collectTests

    def startSubprocess(self, event):
        self.resetIds()
        event.executeTests = self.collectTests
        event.StopTestRunEvent = None

    def _checkError(self, test, testId, mark, msg):
        if test.__class__.__name__ == mark:
            modulename = testId.split(mark)[-1][1:]
            raiser = getattr(test, modulename, None)
            if not raiser:
                return True
            try:
                raiser()
            except Exception:
                logger.exception(msg, modulename)
                return False

        return True

    def collectTests(self, suite, result):
        """Collect tests, but don't run them"""
        for test in suite:
            if isinstance(test, unittest.BaseTestSuite):
                self.collectTests(test, result)
                continue

            testId = test.id()
            # Log the error to trouble shoot the import error:
            if not self._checkError(
                test,
                testId,
                self._importFailureModule,
                "Unable to import the module %s",
            ):
                TestCollector.gotError = True
                continue

            if not self._checkError(
                test,
                testId,
                self._loadTestsFailure,
                "Unable to load tests from directory %s",
            ):
                TestCollector.gotError = True
                continue

            _, testIdUsed = pyunitutils.parseParameterizedTestId(testId)
            self.collectId(testIdUsed)
