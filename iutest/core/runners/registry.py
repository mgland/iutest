# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

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
