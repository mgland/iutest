import os
import inspect


def utestPackageDir():
    filePath = os.path.abspath(inspect.getfile(inspect.currentframe()))
    return os.path.dirname(filePath)


def utestRootDir():
    return os.path.dirname(utestPackageDir())


def isPath(path):
    return "/" in path or "\\" in path
