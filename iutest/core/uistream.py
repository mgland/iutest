import weakref
import re
import sys
import logging
from iutest.core import constants


class UiStream(object):
    _reportUi = None
    _urlTempalte = "<a href='?{1}={2}'>{0}</a>"
    _traceExp = None

    @classmethod
    def register(cls, wgt):
        cls._reportUi = weakref.ref(wgt)

    @classmethod
    def ui(cls):
        if not cls._reportUi:
            return None

        return cls._reportUi()

    @classmethod
    def deregister(cls, wgt):
        if cls.ui() == wgt:
            cls._reportUi = None

    @classmethod
    def _initExp(cls):
        if not cls._traceExp:
            cls._traceExp = re.compile(r"File \"(.*?)\", line (.*?),")

    def __init__(self):
        self._initExp()
        self._testResult = None
        self._linkInfo = None
        self._processStackTraceLink = False
        self._captureStdOut = False

    def setResult(self, result=None):
        self._testResult = result

    def setLinkInfo(self, linkInfo=None):
        self._linkInfo = linkInfo

    def _processLinkInMsg(self, msg):
        if not self._linkInfo:
            return msg

        html = self._urlTempalte.format(*self._linkInfo)
        return msg.replace(self._linkInfo[0], html)

    def _processLinkInStackTrace(self, msg):
        if not self._processStackTraceLink:
            return msg
        lines = msg.split("\n")
        for i, line in enumerate(lines):
            matches = re.finditer(self._traceExp, line)
            if not matches:
                continue

            data = []
            for _, match in enumerate(matches, start=1):
                for groupNum in range(0, len(match.groups())):
                    groupNum = groupNum + 1
                    data.append(match.group(groupNum))

            if not len(data) == 2:
                continue

            html = self._urlTempalte.format(data[0], *data)
            lines[i] = line.replace(data[0], html)
        return "<br>".join(lines)

    def setProcessStackTraceLink(self, process):
        self._processStackTraceLink = process

    def write(self, msg):
        reportUi = self.ui()
        if not reportUi:
            return

        msg = self._processLinkInMsg(msg)
        msg = self._processLinkInStackTrace(msg)

        if self._testResult == constants.TEST_RESULT_ERROR:
            reportUi.logError(msg)

        elif self._testResult == constants.TEST_RESULT_FAIL:
            reportUi.logFailed(msg)

        elif self._testResult == constants.TEST_RESULT_SKIP:
            reportUi.logWarning(msg)

        elif self._testResult == constants.TEST_RESULT_PASS:
            reportUi.logSuccess(msg)

        else:
            reportUi.logInformation(msg)

    def writeln(self, msg=None):
        if msg:
            self.write(msg)
        self.write("<br>")

    def flush(self):
        pass


def writePlainTextToUiStream(msg):
    reportUi = UiStream.ui()
    if reportUi:
        reportUi.logInformation(msg)


class BaseCapturer(object):
    def __init__(self, originalStream):
        self._originalStream = originalStream

    def write(self, msg):
        writePlainTextToUiStream(msg)
        self._originalStream.write(msg)


class StdOutCapturer(BaseCapturer):
    def start(self):
        sys.stdout = self

    def stop(self):
        sys.stdout = self._originalStream


class StdErrCapturer(BaseCapturer):
    def start(self):
        sys.stderr = self

    def stop(self):
        sys.stderr = self._originalStream


class LogHandler(logging.Handler):
    def __init__(self, forcePlainOutput=False):
        logging.Handler.__init__(self)
        self._forcePlainOutput = forcePlainOutput
        self._rootLogger = logging.getLogger()

    def emit(self, record):
        reportUi = UiStream.ui()
        msg = self.format(record)
        if self._forcePlainOutput:
            reportUi.logInformation(msg)
            return

        if record.levelno == logging.WARNING:
            reportUi.logWarning(msg)
        elif record.levelno == logging.ERROR:
            reportUi.logFailed(msg)
        else:
            reportUi.logInformation(msg)

    def start(self):
        self._rootLogger.addHandler(self)

    def stop(self):
        self._rootLogger.removeHandler(self)


class LogCaptureContext(object):
    def __init__(self, forcePlainOutput=False):
        self._handler = LogHandler(forcePlainOutput)

    def __enter__(self):
        self._handler.start()

    def __exit__(self, *_, **__):
        self._handler.stop()
