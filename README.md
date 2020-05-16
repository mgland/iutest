# ![alt text][logo] UTest-0.1
UTest is a python unittest ui based on nose2, with a Chinese Name '油条-0.1'

[logo]: ./icons/utest.svg "UTest Logo"

## Prepare for UTest:
To load UTest UI or run tests, you need to add utest dir path into sys.path:
```python
import sys
testerPath = 'E:/projects/utest'  # Change to your path!
if testerPath not in sys.path:
    sys.path.append(testerPath)
```

## To launch UTest UI:
```python
# Put utest dir into sys.path
import utest
utest.runUi()
```

## To run tests without UI:
```python
# Put utest dir into sys.path
import utest

utest.runAllTests(startDirOrModule='pathToTestRootDir', topDir='pathToPythonTopDir', failEarly=False)
utest.runAllTests(startDirOrModule='package.module1.tests', topDir='pathToPythonTopDir', failEarly=False)

utest.runTests('package.module1.tests.testmodule1', 'package.module1.tests.testmodule2')
```