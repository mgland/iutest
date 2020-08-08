from iutest.core.testrunners import runnerconstants

RUNNER_REGISTRY = {
    runnerconstants.RUNNER_DUMMY : "iutest.core.testrunners.dummyrunner.DummyRunner",
    runnerconstants.RUNNER_NOSE2 : "iutest.core.testrunners.nose2runner.Nose2TestRunner",
    runnerconstants.RUNNER_PYTEST : "iutest.core.testrunners.pytestrunner.PyTestTestRunner",
}