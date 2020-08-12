RUNNER_PYUNIT = 0
RUNNER_NOSE2 = 1
RUNNER_PYTEST = 2

RUNNER_NAMES = {RUNNER_PYUNIT: "unittest", RUNNER_NOSE2: "nose2", RUNNER_PYTEST: "pytest"}


def isValidRunnerName(runnerName):
    return runnerName and runnerName in RUNNER_NAMES.values()


def runnerModeFromName(runnerName):
    for mode, name in RUNNER_NAMES.items():
        if runnerName == name:
            return mode

    return RUNNER_PYUNIT
