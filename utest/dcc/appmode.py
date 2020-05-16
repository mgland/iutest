_APP_MODE_STANDALONE = 'standalone'
_APP_MODE_MAYA = 'maya'

__appMode = None
def appMode():
    global __appMode
    if __appMode is not None:
        return __appMode
        
    __appMode = _APP_MODE_STANDALONE
    try:
        from maya import cmds
        __appMode = _APP_MODE_MAYA
    except Exception:
        pass

    return __appMode


def isInsideMaya():
    return appMode() == _APP_MODE_MAYA


def isStandalone():
    return appMode() == _APP_MODE_STANDALONE
