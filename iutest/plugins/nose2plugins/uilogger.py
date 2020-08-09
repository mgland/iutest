import inspect
import os
import sys
import logging

from iutest import dependencies
from iutest.core import uistream
from iutest.core import pathutils

logger = logging.getLogger(__name__)
nose2 = dependencies.Nose2Wrapper.getModule()
ResultReporter = pathutils.objectFromDotPath("nose2.plugins.result.ResultReporter")

class TestUiLoggerPlugin(ResultReporter):
    """A nose2 plug to capture the logs for ui.
    """

    _originalStdOut = sys.stdout
    _originalStdErr = sys.stderr

    def __init__(self):
        nose2.plugins.result.ResultReporter.__init__(self)
        self.stream = uistream.UiStream()
        self.logHandler = uistream.LogHandler()
        self.stdOutCapturer = uistream.StdOutCapturer(self._originalStdOut)
        self.stdErrCapturer = uistream.StdErrCapturer(self._originalStdErr)

    def startTest(self, event):
        info = self._linkInfoFromTest(event)
        self.stream.setLinkInfo(info)
        nose2.plugins.result.ResultReporter.startTest(self, event)
        self.stream.setLinkInfo()

        self.logHandler.start()
        self.stdOutCapturer.start()
        self.stdErrCapturer.start()

    def testOutcome(self, event):
        self.stdOutCapturer.stop()
        self.stdErrCapturer.stop()
        self.logHandler.stop()

        self.stream.setResult(event.outcome)
        nose2.plugins.result.ResultReporter.testOutcome(self, event)
        self.stream.setResult()

    def afterTestRun(self, event):
        evt = nose2.events.ReportSummaryEvent(event, self.stream, self.reportCategories)

        self.stream.setLinkInfo()
        self.stream.setProcessStackTraceLink(False)

        if evt.stopTestEvent.result.wasSuccessful():
            self.stream.setResult(nose2.result.PASS)
            nose2.plugins.result.ResultReporter.afterTestRun(self, event)
            self.stream.setResult()
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

            self.stream.setResult(nose2.result.FAIL)
            self._printSummary(evt)
            self.stream.setResult()

    def _reportErrorSummary(self, flavour, err):
        self.stream.setProcessStackTraceLink(False)

        desc = self._getDescription(err.test, errorList=True)
        self.stream.setResult(nose2.result.FAIL)
        self.stream.writeln(self.separator1)
        self.stream.setResult()

        self.stream.setLinkInfo(self._linkInfoFromTest(err))
        self.stream.writeln("%s: %s" % (flavour, desc))
        self.stream.setLinkInfo()

        # Now the stack trace, etc:
        self.stream.writeln(self.separator2)
        errDetail = self._getOutcomeDetail(err)
        if errDetail:
            self.stream.setProcessStackTraceLink(True)
            self.stream.writeln(errDetail)
            self.stream.setProcessStackTraceLink(False)

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
