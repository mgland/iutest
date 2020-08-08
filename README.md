# ![alt text][logo] IUTest-0.1
IUTest stands for "Interactive UnitTest", it is a python unittest ui tool that aims to support many unittest frameworks, e.g. nose2, pytest, etc.
It's Chinese name is '油条' :)

[logo]: ./icons/iutest.svg "IUTest Logo"


## To launch IUTest UI:
```python
import sys
testerPath = 'E:/projects/iutest'  # Change to your path!
if testerPath not in sys.path:
    sys.path.append(testerPath)

import iutest
iutest.runUi()
```

## To run tests without UI:
```python
import sys
testerPath = 'D:/projects/iutest'  # Change to your path!
if testerPath not in sys.path:
    sys.path.append(testerPath)
    
import iutest

iutest.runAllTests(startDirOrModule='pathToTestRootDir', topDir='pathToPythonTopDir', stopOnError=False)
iutest.runAllTests(startDirOrModule='iutest.tests', stopOnError=False)

iutest.runTests('iutest.tests.test_dummytests', 'iutest.tests.iutests')
```