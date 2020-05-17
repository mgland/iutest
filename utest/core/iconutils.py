import os
from utest.core import constants
from utest.core import pathutils


def _iconDir():
    return os.path.join(pathutils.utestRootDir(), "icons")


def iconPath(iconName):
    return os.path.join(_iconDir(), iconName)


def iconPathSet(iconName):
    iconDir = _iconDir()
    nameParts = list(iconName.partition("."))
    nameParts.insert(1, None)
    paths = []
    paths.append(os.path.join(iconDir, iconName))
    for suffix in constants.TEST_ICON_SUFFIXES:
        nameParts[1] = suffix
        paths.append(os.path.join(iconDir, "".join(nameParts)))

    return paths
