import logging

from iutest.core import uistream
from iutest.core import constants
from iutest.core import runinfo
from iutest.plugins.pyunitextentions import pyunitcommon

from nose2.plugins import result as resultPlugin  # This has to be imported this way.
from nose2 import result, events  # This has to be imported this way.

logger = logging.getLogger(__name__)


class UiHooksPlugin(resultPlugin.ResultReporter, pyunitcommon.PyUnitUiMixin):
    """A nose2 plug to capture the logs for ui.
    """

    lastRunInfo = runinfo.TestRunInfo()

    def __init__(self):
        resultPlugin.ResultReporter.__init__(self)
        pyunitcommon.PyUnitUiMixin.__init__(self, uistream.UiStream())
        self.Cls = self.__class__

    @classmethod
    def _mapTestResultCode(cls, resultCode, expected):
        """Translate nose2.result result constants to iutest.core.constants.TEST_RESULT_* constants
        """
        if resultCode == result.ERROR:
            return constants.TEST_RESULT_ERROR

        if resultCode == result.FAIL:
            if expected:
                return constants.TEST_RESULT_EXPECTED_FAIL
            return constants.TEST_RESULT_FAIL

        if resultCode == result.SKIP:
            return constants.TEST_RESULT_SKIP

        if resultCode == result.PASS:
            if not expected:
                return constants.TEST_RESULT_UNEXPECTED_PASS
            return constants.TEST_RESULT_PASS

        return constants.TEST_RESULT_NONE

    def startTestRun(self, event):
        self._atStartTestRun()

    def startTest(self, event):
        self._atStartTest(event.test)
        with self.stream.linkInfoCtx(self._linkInfoFromTest(event.test)):
            resultPlugin.ResultReporter.startTest(self, event)

        self._startLogProcessers()

    def stopTest(self, event):
        self._atStopTest(event.test)

    def testOutcome(self, event):
        testId = event.test.id()
        resultCode = self._mapTestResultCode(event.outcome, event.expected)
        self._atOutcomeAvailable(testId, resultCode)

        with self.stream.resultCtx(resultCode):
            resultPlugin.ResultReporter.testOutcome(self, event)

    def stopTestRun(self, event):
        self._atStopTestRun()

    def afterTestRun(self, event):
        evt = events.ReportSummaryEvent(event, self.stream, self.reportCategories)

        self.stream.setLinkInfo()
        self.stream.setProcessStackTraceLink(False)

        if evt.stopTestEvent.result.wasSuccessful():
            with self.stream.resultCtx(self._mapTestResultCode(result.PASS, True)):
                resultPlugin.ResultReporter.afterTestRun(self, event)
        else:
            cats = evt.reportCategories
            errors = cats.get("errors", [])
            failures = cats.get("failures", [])
            for err in errors:
                self._reportErrorSummary("ERROR", err)

            for fail in failures:
                self._reportErrorSummary("FAIL", fail)

            for flavour, events_ in cats.items():
                if flavour in self.dontReport:
                    continue

                for ev in events_:
                    self._reportErrorSummary(flavour.upper(), ev)

            with self.stream.resultCtx(self._mapTestResultCode(result.FAIL, False)):
                self._printSummary(evt)

    def _reportErrorSummary(self, flavour, err):
        self.stream.setProcessStackTraceLink(False)

        desc = self._getDescription(err.test, errorList=True)
        with self.stream.resultCtx(self._mapTestResultCode(result.FAIL, False)):
            self.stream.writeln(self.separator1)

        with self.stream.linkInfoCtx(self._linkInfoFromTest(err.test)):
            self.stream.writeln("%s: %s" % (flavour, desc))

        # Now the stack trace, etc:
        self.stream.writeln(self.separator2)
        errDetail = self._getOutcomeDetail(err)
        if errDetail:
            with self.stream.processStackTraceLinkCtx():
                self.stream.writeln(errDetail)
