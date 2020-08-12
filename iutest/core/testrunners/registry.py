from iutest.core.testrunners import runnerconstants

RUNNER_REGISTRY = {
    runnerconstants.RUNNER_PYUNIT: "iutest.core.testrunners.pyunitrunner.PyUnitRunner",
    runnerconstants.RUNNER_NOSE2: "iutest.core.testrunners.nose2runner.Nose2TestRunner",
    runnerconstants.RUNNER_PYTEST: "iutest.core.testrunners.pytestrunner.PyTestTestRunner",
}


def getRunnerModes():
    """Get all runners in a sorted order.
    """
    return sorted(RUNNER_REGISTRY.keys())
