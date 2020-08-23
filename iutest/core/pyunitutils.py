def parseParameterizedTestId(testId):
    isParameterized = ":" in testId
    return (
        (isParameterized, testId.split(":")[0])
        if isParameterized
        else (isParameterized, testId)
    )
