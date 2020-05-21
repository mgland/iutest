from utest import qt


def findParentWindow():
    return qt.findTopLevelWidgetByName("MayaWindow")
