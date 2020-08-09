import os
import inspect
import logging
import sys
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
    def tryImportClosestModule(paths):
        module = None
        while paths:
            try:
                module = __import__('.'.join(paths))
                break
            except:
                del paths[-1]
                if not paths:
                    return None
        return module

    parts = dotPath.split('.')
    module = tryImportClosestModule(parts[:])
    if not module:
        logger.error("No module found from %s", dotPath)
        return None

    # Now get the object from the module:
    obj = module
    for part in parts[1:]:
        try:
            obj = getattr(obj, part)
        except AttributeError:
            logger.exception("Error importing the module at path %s", dotPath)
            return None

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
