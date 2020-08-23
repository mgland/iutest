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
