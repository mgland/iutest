

RUNNER_NOSE2 = 0
RUNNER_PYTEST = 1

RUNNER_REGISTRY = {
    RUNNER_NOSE2 : "iutest.core.testrunners.nose2runner.Nose2TestRunner",
    RUNNER_PYTEST : "iutest.core.testrunners.pytestrunner.PyTestTestRunner",
}