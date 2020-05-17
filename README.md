# ![alt text][logo] UTest-0.1
UTest is a python unittest ui based on nose2, with a Chinese Name '油条-0.1'

[logo]: ./icons/utest.svg "UTest Logo"


## To launch UTest UI:
```python
import sys
testerPath = 'E:/projects/utest'  # Change to your path!
if testerPath not in sys.path:
    sys.path.append(testerPath)
import utest
utest.runUi()
```

## To run tests without UI:
```python
import sys
testerPath = 'E:/projects/utest'  # Change to your path!
if testerPath not in sys.path:
    sys.path.append(testerPath)
import utest

utest.runAllTests(startDirOrModule='pathToTestRootDir', topDir='pathToPythonTopDir', stopOnError=False)
utest.runAllTests(startDirOrModule='package.module1.tests', topDir='pathToPythonTopDir', stopOnError=False)

utest.runTests('package.module1.tests.testmodule1', 'package.module1.tests.testmodule2')
```