from iutest import qt


def findParentWindow():
    return qt.findTopLevelWidgetByName("MayaWindow")
