# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from iutest import qt as _qt

_APP_MODE_STANDALONE = "standalone"
_APP_MODE_MAYA = "maya"

__appMode = None


def appMode():
    global __appMode
    if __appMode is not None:
        return __appMode

    __appMode = _APP_MODE_STANDALONE
    try:
        import maya
    except:
        pass
    else:
        __appMode = _APP_MODE_MAYA

    return __appMode


def isInsideMaya():
    return appMode() == _APP_MODE_MAYA


def isStandalone():
    return appMode() == _APP_MODE_STANDALONE


def _dccModule():
    if isStandalone():
        from iutest.dcc import standalone

        return standalone
    elif isInsideMaya():
        from iutest.dcc import dccmaya

        return dccmaya


module = _dccModule()
findParentWindow = module.findParentWindow
