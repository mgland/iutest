import inspect
import os
import sys
import logging

from iutest import dependencies
from iutest.core import uistream
from iutest.core import constants
from iutest.core import pathutils

from nose2.plugins import result as resultPlugin  # This has to be imported this way.
from nose2 import result, events, util  # This has to be imported this way.

logger = logging.getLogger(__name__)


class TestUiLoggerPlugin(resultPlugin.ResultReporter):
    """A nose2 plug to capture the logs for ui.
    """

    _originalStdOut = sys.stdout
    _originalStdErr = sys.stderr

    def __init__(self):
        resultPlugin.ResultReporter.__init__(self)
        self.stream = uistream.UiStream()
        self.logHandler = uistream.LogHandler()
        self.stdOutCapturer = uistream.StdOutCapturer(self._originalStdOut)
        self.stdErrCapturer = uistream.StdErrCapturer(self._originalStdErr)

    @classmethod
    def _mapTestResultCode(cls, nose2ResultCode):
        """Translate nose2.result result constants to iutest.core.constants.TEST_RESULT_* constants
        """
        if nose2ResultCode == result.ERROR:
            return constants.TEST_RESULT_ERROR
        elif nose2ResultCode == result.FAIL:
            return constants.TEST_RESULT_FAIL
        elif nose2ResultCode == result.SKIP:
            return constants.TEST_RESULT_SKIP
        elif nose2ResultCode == result.PASS:
            return constants.TEST_RESULT_PASS
        else:
            return None

    def startTest(self, event):
        with self.stream.linkInfoCtx(self._linkInfoFromTest(event)):
            resultPlugin.ResultReporter.startTest(self, event)

        self.logHandler.start()
        self.stdOutCapturer.start()
        self.stdErrCapturer.start()

    def testOutcome(self, event):
        self.stdOutCapturer.stop()
        self.stdErrCapturer.stop()
        self.logHandler.stop()

        with self.stream.resultCtx(self._mapTestResultCode(event.outcome)):
            resultPlugin.ResultReporter.testOutcome(self, event)

    def afterTestRun(self, event):
        evt = events.ReportSummaryEvent(event, self.stream, self.reportCategories)

        self.stream.setLinkInfo()
        self.stream.setProcessStackTraceLink(False)

        if evt.stopTestEvent.result.wasSuccessful():
            with self.stream.resultCtx(self._mapTestResultCode(result.PASS)):
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

            with self.stream.resultCtx(self._mapTestResultCode(result.FAIL)):
                self._printSummary(evt)

    def _reportErrorSummary(self, flavour, err):
        self.stream.setProcessStackTraceLink(False)

        desc = self._getDescription(err.test, errorList=True)
        with self.stream.resultCtx(self._mapTestResultCode(result.FAIL)):
            self.stream.writeln(self.separator1)

        with self.stream.linkInfoCtx(self._linkInfoFromTest(err)):
            self.stream.writeln("%s: %s" % (flavour, desc))

        # Now the stack trace, etc:
        self.stream.writeln(self.separator2)
        errDetail = self._getOutcomeDetail(err)
        if errDetail:
            with self.stream.processStackTraceLinkCtx():
                self.stream.writeln(errDetail)

    def _linkInfoFromTest(self, event):
        try:
            testMethodName = event.test.id().split(".")[-1]
            test = getattr(event.test, testMethodName)
            sourceFile, line = pathutils.sourceFileAndLineFromObject(test)
            if not sourceFile:  # os.path.isfile(sourceFile)
                return None

            return testMethodName, sourceFile, line
        except:
            logger.debug("Unable retrieve test information for quick navigation.")
        return None
