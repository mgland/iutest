# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import unittest

from iutest import qt as _qt


@unittest.skipUnless(_qt.checkQtAvailability(), "Qt is not available")
class GoToCodeTestCase(unittest.TestCase):
    def setUp(self):
        self._path = "/path/to/source.py"
        self._line = 21

    def test_saveRestore(self):
        from iutest.core import gotocode

        data = {
            'code --goto "$file":$line': 'code --goto "/path/to/source.py":21',
            'notepad "$file"': 'notepad "/path/to/source.py"',
            'vim +$line "$file"': 'vim +21 "/path/to/source.py"',
        }
        for template, expected in data.items():
            self.assertEqual(
                gotocode.CodeLineVisitor._goToCmd(template, self._path, self._line),
                expected,
            )
