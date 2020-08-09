import os
from iutest.core import constants
from iutest.core import pathutils


def _iconDir():
    return os.path.join(pathutils.iutestPackageDir(), "icons")


def iconPath(iconName):
    return os.path.join(_iconDir(), iconName)


def iconPathSet(iconName, suffixes, includeInput=True):
    iconDir = _iconDir()
    nameParts = list(iconName.partition("."))
    nameParts.insert(1, None)
    paths = []
    if includeInput:
        paths.append(os.path.join(iconDir, iconName))
    for suffix in suffixes:
        nameParts[1] = suffix
        fileName = "".join(nameParts)
        paths.append(os.path.join(iconDir, fileName))

    return paths
