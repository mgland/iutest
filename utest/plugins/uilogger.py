import inspect
import os
import sys
import logging

from nose2.plugins import result as resultPlugin  # This has to be imported this way.
from nose2 import result, events, util  # This has to be imported this way.
from utest.core import uistream

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

    def startTest(self, event):
        info = self._linkInfoFromTest(event)
        self.stream.setLinkInfo(info)
        resultPlugin.ResultReporter.startTest(self, event)
        self.stream.setLinkInfo()

        self.logHandler.start()
        self.stdOutCapturer.start()
        self.stdErrCapturer.start()

    def testOutcome(self, event):
        self.stdOutCapturer.stop()
        self.stdErrCapturer.stop()
        self.logHandler.stop()

        self.stream.setResult(event.outcome)
        resultPlugin.ResultReporter.testOutcome(self, event)
        self.stream.setResult()

    def afterTestRun(self, event):
        evt = events.ReportSummaryEvent(event, self.stream, self.reportCategories)

        self.stream.setLinkInfo()
        self.stream.setProcessStackTraceLink(False)

        if evt.stopTestEvent.result.wasSuccessful():
            self.stream.setResult(result.PASS)
            resultPlugin.ResultReporter.afterTestRun(self, event)
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

            self.stream.setResult(result.FAIL)
            self._printSummary(evt)
            self.stream.setResult()

    def _reportErrorSummary(self, flavour, err):
        self.stream.setProcessStackTraceLink(False)

        desc = self._getDescription(err.test, errorList=True)
        self.stream.setResult(result.FAIL)
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
            sourceFile = inspect.getsourcefile(event.test.__class__)
            if not sourceFile:  # os.path.isfile(sourceFile)
                return None

            try:
                line = inspect.getsourcelines(test)[-1]
            except:
                line = 0
            return (testMethodName, sourceFile, line)
        except:
            logger.debug("Unable retrieve test information for quick navigation.")
        return None
