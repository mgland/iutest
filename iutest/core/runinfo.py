class TestRunInfo(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.runTestIds = []    # The ids here will all be unique.
        self.runCount = 0       # The count here will be the actually test run, including potential duplicated.
        self.failedTestId = None
        self.successCount = 0
        self.failedCount = 0
        self.errorCount = 0
        self.skipCount = 0
        self.expectedFailureCount = 0
        self.unexpectedSuccessCount = 0

        self._sessionStartTime = 0
        self.sessionRunTime = 0

        self._testStartTimes = {}
        self.singleTestRunTime = 0
