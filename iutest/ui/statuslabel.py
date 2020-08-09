from iutest.qt import QtWidgets, QtCore
from iutest.ui import uiconstants


class StatusLabel(QtWidgets.QLabel):
    def __init__(self, parent):
        QtWidgets.QLabel.__init__(self, parent)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self._testManager = None

    def setTestManager(self, manager):
        self._testManager = manager

    def updateReport(self):
        runInfo = self._testManager.lastRunInfo()
        testLbl = "tests" if runInfo.lastRunCount != 1 else "test"
        msgs = [
            "%s %s run in %.3f sec"
            % (runInfo.lastRunCount, testLbl, runInfo.lastRunTime)
        ]
        if runInfo.lastSuccessCount == runInfo.lastRunCount:
            msgs.append(
                "<font color=%s>ALL GOOD :)</font>"
                % uiconstants.LOG_COLOR_SUCCESS.name()
            )
        else:
            if runInfo.lastFailedCount:
                msgs.append(
                    "<font color=%s>%s failed</font>"
                    % (uiconstants.LOG_COLOR_FAILED.name(), runInfo.lastFailedCount)
                )
            if runInfo.lastErrorCount:
                msgs.append(
                    "<font color=%s>%s errors</font>"
                    % (uiconstants.LOG_COLOR_ERROR.name(), runInfo.lastErrorCount)
                )
            if runInfo.lastSkipCount:
                msgs.append(
                    "<font color=%s>%s skipped</font>"
                    % (uiconstants.LOG_COLOR_WARNING.name(), runInfo.lastSkipCount)
                )
            if runInfo.lastExpectedFailureCount:
                msgs.append(
                    "<font color=%s>%s expected failures</font>"
                    % (
                        uiconstants.LOG_COLOR_SUCCESS.name(),
                        runInfo.lastExpectedFailureCount,
                    )
                )
            if runInfo.lastUnexpectedSuccessCount:
                msgs.append(
                    "<font color=%s>%s unexpected successes</font>"
                    % (
                        uiconstants.LOG_COLOR_ERROR.name(),
                        runInfo.lastUnexpectedSuccessCount,
                    )
                )
        self.setText(", ".join(msgs))

    def reportTestCount(self, testCount):
        self.setText("{} tests.".format(testCount))

    def startCollectingTests(self):
        self.setText("Loading tests...")
        self.repaint()
