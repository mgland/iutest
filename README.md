# ![logo] IUTest
"IUTest" stands for "Interactive UnitTest", it is an interactive python unit-test runner that aims to support various unit-test frameworks like
[nose2](https://pypi.org/project/nose2/), [pytest](https://pypi.org/project/pytest/), etc.

In Chinese it is called "[You Tiao](https://en.wikipedia.org/wiki/Youtiao)", which is Chinese fried breadstick typically for breakfast :)

[logo]: ./icons/iutest.svg "IUTest Logo"


### To install IUTest
```shell
# For system default python or virtual env
pip install iutest

# For pipenv python
pipenv install iutest
```

### IUTest Command Line Interface
```shell
# Get version:
iutest --version

# Run IUTest UI:
iutest --ui

# Run all tests for python module or directory:
iutest --runner "nose2" --runAllTests "iutest" 

# Run tests by python module paths:
iutest --runner "nose2" --runTest "iutest.tests.test_dummypyunits" --runTest "iutest.tests.iutests"
```

### Run in python
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

# Run UI:
iutest.runUi()
```

### Run IUTest in DCC application, e.g. [Maya](https://www.autodesk.com.au/products/maya)
There might be a way to use pip with Maya, but here we keep it simple.
- Download IUTest and its dependency libraries, 
  including [nose2](https://pypi.org/project/nose2/), [pytest](https://pypi.org/project/pytest/) and [reimport](https://pypi.org/project/reimport/), 
  these are all available from [PyPi](https://pypi.org/)
- Install the [code](#Run-in-python) above as a Maya shelf button.
- Click on the shelf button to run IUTest UI.
