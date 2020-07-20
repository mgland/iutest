
class BaseTestRunner(object):
    def __init__(self, manager):
        self._manager = manager

    @classmethod
    def name(cls):
        cls._raiseNotImplementedError()

    @classmethod
    def _raiseNotImplementedError(cls):
        raise NotImplementedError("You should not use {} directly.".format(cls.__name__))

    def runTests(self, *testIds):
        self._raiseNotImplementedError()

    def runSingleTestPartially(self, testId, partialMode):
        """Run partial steps of test, like running setUp only, or setUp and test but without teardown.
        Args:
            testId (str): id of test, the python module.
            partialMode (int): the test run mode, available values are:
                constants.RUN_TEST_SETUP_ONLY | constants.RUN_TEST_NO_TEAR_DOWN
        """
        self._raiseNotImplementedError()

    def iterAllTestIds(self, startDir, topDir):
        self._raiseNotImplementedError()

