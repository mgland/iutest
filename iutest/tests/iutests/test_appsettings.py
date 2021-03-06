# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import unittest

from iutest.core import appsettings
from iutest import qt as _qt


@unittest.skipUnless(_qt.checkQtAvailability(), "Qt is not available")
class AppSettingsTestCase(unittest.TestCase):
    def test_saveRestore(self):
        setting = appsettings.AppSettings.get()
        data = {
            "testInt": (1, 1),
            "testInt1": (True, 1),
            "testInt2": ("1", 1),
            "testBool": (True, True),
            "testBool1": (1, True),
            "testBool2": ("1", True),
            "testStr": ("str", "str"),
            "testStr1": (1, "1"),
            "testStr2": ("", ""),
        }
        for key, (inputValue, _) in data.items():
            setting.saveSimpleConfig(key, inputValue, sync=False)

        for key, (inputValue, expectedValue) in data.items():
            self.assertEqual(setting.simpleConfigValue(key), inputValue)

            if "Int" in key:
                self.assertEqual(setting.simpleConfigIntValue(key), expectedValue)

            elif "Bool" in key:
                self.assertEqual(setting.simpleConfigBoolValue(key), expectedValue)

            elif "Str" in key:
                self.assertEqual(setting.simpleConfigStrValue(key), expectedValue)

        for key in data:
            setting.removeConfig(key)
            self.assertTrue(setting.simpleConfigValue(key) is None)
