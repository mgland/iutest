import os
import inspect
import nose2
import logging

logger = logging.getLogger(__name__)


def utestPackageDir():
    filePath = os.path.abspath(inspect.getfile(inspect.currentframe()))
    return os.path.dirname(os.path.dirname(filePath))


def utestRootDir():
    return os.path.dirname(utestPackageDir())


def isPath(path):
    return "/" in path or "\\" in path


def objectFromDotPath(dotPath):
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
