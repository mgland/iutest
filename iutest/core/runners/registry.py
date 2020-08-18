from iutest.core.runners import runnerconstants

RUNNER_REGISTRY = {
    runnerconstants.RUNNER_PYUNIT: "iutest.core.runners.pyunitrunner.PyUnitRunner",
    runnerconstants.RUNNER_NOSE2: "iutest.core.runners.nose2runner.Nose2TestRunner",
    runnerconstants.RUNNER_PYTEST: "iutest.core.runners.pytestrunner.PyTestTestRunner",
}


def getRunnerModes():
    """Get all runners in a sorted order.
    """
    return sorted(RUNNER_REGISTRY.keys())
