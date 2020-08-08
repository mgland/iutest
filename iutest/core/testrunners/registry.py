

RUNNER_DUMMY = 0
RUNNER_NOSE2 = 1
RUNNER_PYTEST = 2

RUNNER_REGISTRY = {
    RUNNER_DUMMY : "iutest.core.testrunners.dummyrunner.DummyRunner",
    RUNNER_NOSE2 : "iutest.core.testrunners.nose2runner.Nose2TestRunner",
    RUNNER_PYTEST : "iutest.core.testrunners.pytestrunner.PyTestTestRunner",
}