from utest.qt import QtWidgets, QtCore
from utest.plugins import viewupdater
from utest.ui import uiconstants


class StatusLabel(QtWidgets.QLabel):
    def __init__(self, parent):
        QtWidgets.QLabel.__init__(self, parent)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

    def updateReport(self):
        testLbl = "tests" if viewupdater.ViewUpdater.lastRunCount != 1 else "test"
        msgs = [
            "%s %s run in %.3f sec"
            % (
                viewupdater.ViewUpdater.lastRunCount,
                testLbl,
                viewupdater.ViewUpdater.runTime,
            )
        ]
        if (
            viewupdater.ViewUpdater.lastSuccessCount
            == viewupdater.ViewUpdater.lastRunCount
        ):
            msgs.append(
                "<font color=%s>ALL GOOD :)</font>" % uiconstants.LOG_COLOR_SUCCESS.name()
            )
        else:
            if viewupdater.ViewUpdater.lastFailedCount:
                msgs.append(
                    "<font color=%s>%s failed</font>"
                    % (
                        uiconstants.LOG_COLOR_FAILED.name(),
                        viewupdater.ViewUpdater.lastFailedCount,
                    )
                )
            if viewupdater.ViewUpdater.lastErrorCount:
                msgs.append(
                    "<font color=%s>%s errors</font>"
                    % (
                        uiconstants.LOG_COLOR_ERROR.name(),
                        viewupdater.ViewUpdater.lastErrorCount,
                    )
                )
            if viewupdater.ViewUpdater.lastSkipCount:
                msgs.append(
                    "<font color=%s>%s skipped</font>"
                    % (
                        uiconstants.LOG_COLOR_WARNING.name(),
                        viewupdater.ViewUpdater.lastSkipCount,
                    )
                )
            if viewupdater.ViewUpdater.lastExpectedFailureCount:
                msgs.append(
                    "<font color=%s>%s expected failures</font>"
                    % (
                        uiconstants.LOG_COLOR_SUCCESS.name(),
                        viewupdater.ViewUpdater.lastExpectedFailureCount,
                    )
                )
            if viewupdater.ViewUpdater.lastUnexpectedSuccessCount:
                msgs.append(
                    "<font color=%s>%s unexpected successes</font>"
                    % (
                        uiconstants.LOG_COLOR_ERROR.name(),
                        viewupdater.ViewUpdater.lastUnexpectedSuccessCount,
                    )
                )
        self.setText(", ".join(msgs))

    def reportTestCount(self, testCount):
        self.setText("{} tests.".format(testCount))
