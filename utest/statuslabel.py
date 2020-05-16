from utest.qt import QtWidgets, QtCore
from utest import constants
from utest.plugins import viewupdater


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
                "<font color=%s>ALL GOOD :)</font>" % constants.LOG_COLOR_SUCCESS.name()
            )
        else:
            if viewupdater.ViewUpdater.lastFailedCount:
                msgs.append(
                    "<font color=%s>%s failed</font>"
                    % (
                        constants.LOG_COLOR_FAILED.name(),
                        viewupdater.ViewUpdater.lastFailedCount,
                    )
                )
            if viewupdater.ViewUpdater.lastErrorCount:
                msgs.append(
                    "<font color=%s>%s errors</font>"
                    % (
                        constants.LOG_COLOR_ERROR.name(),
                        viewupdater.ViewUpdater.lastErrorCount,
                    )
                )
            if viewupdater.ViewUpdater.lastSkipCount:
                msgs.append(
                    "<font color=%s>%s skipped</font>"
                    % (
                        constants.LOG_COLOR_WARNING.name(),
                        viewupdater.ViewUpdater.lastSkipCount,
                    )
                )
        self.setText(", ".join(msgs))

    def reportTestCount(self, testCount):
        self.setText("{} tests.".format(testCount))
