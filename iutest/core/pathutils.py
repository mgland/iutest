import os
import inspect
import logging

logger = logging.getLogger(__name__)


def iutestPackageDir():
    filePath = os.path.abspath(inspect.getfile(inspect.currentframe()))
    return os.path.dirname(os.path.dirname(filePath))


def iutestRootDir():
    return os.path.dirname(iutestPackageDir())


def isPath(path):
    return "/" in path or "\\" in path


def objectFromDotPath(dotPath):
    import nose2
    _, obj = nose2.util.object_from_name(dotPath)
    return obj


def sourceFileAndLineFromObject(obj):
    sourceFile = inspect.getsourcefile(obj)
    if not sourceFile:
        return (None, None)

    try:
        line = inspect.getsourcelines(obj)[-1]
    except:
        line = 0

    return sourceFile, line
