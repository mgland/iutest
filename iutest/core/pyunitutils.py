# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.


def parseParameterizedTestId(testId):
    isParameterized = ":" in testId
    return (
        (isParameterized, testId.split(":")[0])
        if isParameterized
        else (isParameterized, testId)
    )
