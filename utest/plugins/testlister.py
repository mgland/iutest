import unittest
import logging
import nose2  # This has to be imported this way.

from utest.core import pathutils

logger = logging.getLogger(__name__)


def iterAllTestPathsFromRootDir(startDirOrModuleName, topDir=None):
    argv = [
        "nose2",
        "--plugin",
        "utest.plugins.testlister",
        "--list-tests",
        "--plugin",
        "nose2.plugins.loader.eggdiscovery",
        "--plugin",
        "utest.plugins.removeduplicated",
        "--exclude-plugin",
        "nose2.plugins.result",
    ]
    if pathutils.isPath(startDirOrModuleName):
        argv.extend(["-s", startDirOrModuleName, "-t", topDir])
    else:
        argv.append(startDirOrModuleName)

    nose2.discover(argv=argv, exit=False)
    for tid in TestCollector.iterTestIds():
        yield tid


def parseParameterizedTestId(testId):
    isParameterized = ":" in testId
    return (
        (isParameterized, testId.split(":")[0])
        if isParameterized
        else (isParameterized, testId)
    )


class TestCollector(nose2.events.Plugin):
    """A nose2 plug to collect the tests without running them.
    """

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
                print(self._errorSeparator)
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
                continue

            if not self._checkError(
                test,
                testId,
                self._loadTestsFailure,
                "Unable to load tests from directory %s",
            ):
                continue

            _, testIdUsed = parseParameterizedTestId(testId)
            self.collectId(testIdUsed)
