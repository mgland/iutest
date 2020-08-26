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


def _iterAllPythonSourceFiles(rootdir):
    # for py-2 compatibility we cannot use glob.iglob or os.scandir.
    for root, directories, files in os.walk(rootdir):
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(root, f)

    for subDir in directories:
        for f in _iterAllPythonSourceFiles(subDir):
            yield f


def addCopyrightHeader():
    copyRightLines = _getCopyrightHeader()
    copyRightStr = "".join(copyRightLines)
    rootdir = os.path.dirname(__file__)

    excludedFolder = os.path.join(rootdir, "build")

    for filename in _iterAllPythonSourceFiles(rootdir):
        if filename == __file__ or filename.startswith(excludedFolder):
            continue

        with open(filename, "r") as f:
            data = f.read()

        if data.startswith(copyRightLines[0]):
            continue

        with open(filename, "w") as f:
            f.write(copyRightStr + "\n" + data)
            print("Prepend copyright header: {}".format(filename))


if __name__ == "__main__":
    addCopyrightHeader()
