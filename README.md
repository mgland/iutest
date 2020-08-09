# ![alt text][logo] IUTest-0.1
IUTest stands for "Interactive UnitTest", it is a python unittest ui tool that aims to support many unittest frameworks, e.g. nose2, pytest, etc.
It's Chinese name is '油条' :)

[logo]: ./icons/iutest.svg "IUTest Logo"


### To install IUTest:
```shell
# For system default python or virtual env
pip install iutest

# For pipenv python
pipenv install iutest
```

### To run tests without UI in python:
```python
import sys
testerPath = 'E:/projects/iutest'  # Change to your path!
if testerPath not in sys.path:
    sys.path.append(testerPath)
    
import iutest
# Run all tests under given file system path:
iutest.runAllTests(startDirOrModule='pathToTestRootDir', topDir='pathToPythonTopDir', stopOnError=False)

# Run all tests by given python module path:
iutest.runAllTests(startDirOrModule='iutest.tests', stopOnError=False)

# Run tests by given python module paths:
iutest.runTests('iutest.tests.test_dummytests', 'iutest.tests.iutests')
```

### To install and run IUTest for DCC application, e.g. Maya:
- They might be a way to use pip with Maya, but normally, you just download IUTest and its dependency libraries : nose2 or pytest, reimport, all these are available from https://pypi.org/
- Install the code below as a Maya shelf button:
```python
import sys
testerPath = 'E:/projects/iutest'  # Change to your path!
if testerPath not in sys.path:
    sys.path.append(testerPath)

import iutest
iutest.runUi()
```
- Click on the shelf button to run IUTest UI.
