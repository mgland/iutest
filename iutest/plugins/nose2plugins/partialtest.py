# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import unittest
import logging
import nose2

from iutest.core import constants

logger = logging.getLogger(__name__)


class _NoTearDown(object):
    def __init__(self, test):
        self._test = test
        self._originalTearDown = test.tearDown

    def _dummyTearDown(self):
        logger.info("Skipped %s.tearDown().", self._test.__class__.__name__)

    def __enter__(self):
        self._test.tearDown = self._dummyTearDown

    def __exit__(self, *args, **kwargs):
        self._test.tearDown = self._originalTearDown


class PartialTestRunner(nose2.events.Plugin):
    """A nose2 plug to run parts of single test, like run only setup, setup+test, etc.
    """

    commandLineSwitch = (None, "partial-test", "Run partial test.")
    runMode = constants.RUN_TEST_SETUP_ONLY

    lastRunTest = None

    @classmethod
    def setRunMode(cls, mode):
        """Set run mode to either TEST_SETUP_ONLY or TEST_NO_TEAR_DOWN
        """
        cls.runMode = min(
            constants.RUN_TEST_FULL, max(constants.RUN_TEST_SETUP_ONLY, int(mode))
        )

    def registerInSubprocess(self, event):
        event.pluginClasses.append(self.__class__)

    def startTestRun(self, event):
        PartialTestRunner.lastRunTest = None
        event.executeTests = self.runPartialTest

    def startSubprocess(self, event):
        PartialTestRunner.lastRunTest = None
        event.executeTests = self.runPartialTest
        event.StopTestRunEvent = None

    def _runPartialTest(self, test):
        if self.runMode == constants.RUN_TEST_SETUP_ONLY:
            test.setUp()
            logger.info("Run %s.setUp() only.", test.__class__.__name__)
        elif self.runMode == constants.RUN_TEST_NO_TEAR_DOWN:
            with _NoTearDown(test):
                test.run(self.session.testResult)
        else:
            test.run(self.session.testResult)

        PartialTestRunner.lastRunTest = test

    def stopTestRun(self, event):
        if self.lastRunTest:
            event.result.shouldStop = True

    def runPartialTest(self, suite, result):
        """Collect tests, but don't run them"""
        for test in suite:
            if isinstance(test, unittest.BaseTestSuite):
                self.runPartialTest(test, result)
                continue

            self._runPartialTest(test)
            return
