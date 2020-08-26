# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import os
import glob


def _getCopyrightHeader():
    copyRightLines = []
    with open(__file__, "r") as f:
        for l in f:
            if l.startswith("#"):
                copyRightLines.append(str(l))
            else:
                break

    return copyRightLines


def addCopyrightHeader():
    copyRightLines = _getCopyrightHeader()
    copyRightStr = "".join(copyRightLines)
    rootdir = os.path.dirname(__file__)

    excludedFolder = os.path.join(rootdir, "build", "")

    for filename in glob.iglob(rootdir + "/**/*.py", recursive=True):
        if filename == __file__ or filename.startswith(excludedFolder):
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
