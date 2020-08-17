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
        testLbl = "tests" if runInfo.runCount != 1 else "test"
        msgs = [
            "%s %s run in %.3f sec"
            % (runInfo.runCount, testLbl, runInfo.sessionRunTime)
        ]
        if runInfo.successCount == runInfo.runCount:
            msgs.append(
                "<font color=%s>ALL GOOD :)</font>"
                % uiconstants.LOG_COLOR_SUCCESS.name()
            )
        else:
            if runInfo.failedCount:
                msgs.append(
                    "<font color=%s>%s failed</font>"
                    % (uiconstants.LOG_COLOR_FAILED.name(), runInfo.failedCount)
                )
            if runInfo.errorCount:
                msgs.append(
                    "<font color=%s>%s errors</font>"
                    % (uiconstants.LOG_COLOR_ERROR.name(), runInfo.errorCount)
                )
            if runInfo.skipCount:
                msgs.append(
                    "<font color=%s>%s skipped</font>"
                    % (uiconstants.LOG_COLOR_WARNING.name(), runInfo.skipCount)
                )
            if runInfo.expectedFailureCount:
                msgs.append(
                    "<font color=%s>%s expected failures</font>"
                    % (
                        uiconstants.LOG_COLOR_SUCCESS.name(),
                        runInfo.expectedFailureCount,
                    )
                )
            if runInfo.unexpectedSuccessCount:
                msgs.append(
                    "<font color=%s>%s unexpected successes</font>"
                    % (
                        uiconstants.LOG_COLOR_ERROR.name(),
                        runInfo.unexpectedSuccessCount,
                    )
                )
        self.setText(", ".join(msgs))

    def reportTestCount(self, testCount):
        self.setText("{} tests.".format(testCount))

    def startCollectingTests(self):
        self.setText("Loading tests...")
        self.repaint()
