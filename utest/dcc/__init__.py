from utest.dcc import appmode

if appmode.isStandalone():
    from utest.dcc import standalone as dcc
elif appmode.isInsideMaya():
    from utest.dcc import maya as dcc

findParentWindow = dcc.findParentWindow
