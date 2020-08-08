import os
import inspect
import logging
from iutest import dependencies

logger = logging.getLogger(__name__)


def iutestPackageDir():
    filePath = os.path.abspath(inspect.getfile(inspect.currentframe()))
    return os.path.dirname(os.path.dirname(filePath))


def iutestRootDir():
    return os.path.dirname(iutestPackageDir())


def isPath(path):
    return "/" in path or "\\" in path


def objectFromDotPath(dotPath):
    result = dependencies.Nose2Wrapper.get().util.object_from_name(dotPath)
    return result[-1]


def sourceFileAndLineFromObject(obj):
    sourceFile = inspect.getsourcefile(obj)
    if not sourceFile:
        return (None, None)

    try:
        line = inspect.getsourcelines(obj)[-1]
    except:
        line = 0

    return sourceFile, line
