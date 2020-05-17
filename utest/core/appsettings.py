import collections
from utest.core import constants
from utest.qt import QtCore


def get():
    return AppSettings.get()


class SettingsGroupContext(object):
    def __init__(self, groupName):
        self._groupName = groupName
        self._settings = AppSettings.get()

    def __enter__(self):
        self._settings.beginGroup(self._groupName)
        return self._settings
    
    def __exit__(self, *_, **__):
        self._settings.endGroup()


class AppSettings(object):
    _instance = None

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = AppSettings()
        return cls._instance
    
    @staticmethod
    def createIniSettings():
        return QtCore.QSettings(
            QtCore.QSettings.IniFormat,
            QtCore.QSettings.UserScope,
            constants.ORG_MGLAND,
            constants.APP_NAME,
        )

    def __init__(self):
        self._settings = self.createIniSettings()

    def saveSimpleConfig(self, key, value, sync=True):
        self._qsettings().setValue(key, value)
        if sync:
            self._qsettings().sync()

    def simpleConfigValue(self, key):
        return self._qsettings().value(key)

    def removeConfig(self, key):
        self._qsettings().remove(key)

    def _qsettings(self):
        return object.__getattribute__(self, "_settings")

    def __getattribute__(self, attr):
        """We deligate everything else to QSettings object.
        """
        if hasattr(AppSettings, attr):
            return object.__getattribute__(self, attr)

        settingsObj = object.__getattribute__(self, "_qsettings")()
        return getattr(settingsObj, attr)
    