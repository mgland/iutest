# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import os


def _getCopyrightHeader():
    copyRightLines = []
    with open(__file__, "r") as f:
        for l in f:
            if l.startswith("#"):
                copyRightLines.append(str(l))
            else:
                break

    return copyRightLines


def _iterAllPythonSourceFiles(rootdir, excludedDirPath):
    # for py-2 and py-3 compatibility we cannot use glob.iglob.
    subfolders = []

    for f in os.scandir(rootdir):
        if f.is_dir():
            subfolders.append(f.path)

        if f.is_file():
            if f.name.endswith(".py"):
                yield f.path

    for subDir in subfolders:
        if subDir == excludedDirPath:
            continue

        for f in _iterAllPythonSourceFiles(subDir, excludedDirPath):
            yield f


def addCopyrightHeader():
    copyRightLines = _getCopyrightHeader()
    copyRightStr = "".join(copyRightLines)
    rootdir = os.path.dirname(__file__)

    excludedFolder = os.path.join(rootdir, "build")

    for filename in _iterAllPythonSourceFiles(rootdir, excludedFolder):
        if filename == __file__:
            continue

        with open(filename, "r") as f:
            data = f.read()

        if data.startswith(copyRightLines[0]):
            continue

        with open(filename, "w") as f:
            f.write(copyRightStr + "\n" + data)
            print("Append copyright header for {}".format(filename))


if __name__ == "__main__":
    addCopyrightHeader()
