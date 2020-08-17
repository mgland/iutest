class TestRunInfo(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.runTestIds = []
        self.failedTestId = None
        self.runCount = 0
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