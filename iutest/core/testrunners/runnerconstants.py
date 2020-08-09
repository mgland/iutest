RUNNER_DUMMY = 0
RUNNER_NOSE2 = 1
RUNNER_PYTEST = 2

RUNNER_NAMES = {
    RUNNER_DUMMY : '',
    RUNNER_NOSE2 : 'nose2',
    RUNNER_PYTEST : 'pytest',
}


def isValidRunnerName(runnerModeName):
    return runnerModeName and runnerModeName in RUNNER_NAMES.values()


def runnerModeFromName(runnerModeName):
    for mode, name in RUNNER_NAMES.items():
        if runnerModeFromName == name:
            return mode

    return RUNNER_DUMMY