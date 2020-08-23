import collections
import logging
from iutest.core import constants
from iutest.qt import QtCore, variantToPyValue

logger = logging.getLogger(__name__)


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
    def _createIniSettings():
        return QtCore.QSettings(
            QtCore.QSettings.IniFormat,
            QtCore.QSettings.UserScope,
            constants.ORG_MGLAND,
            constants.APP_NAME,
        )

    def __init__(self):
        self._settings = self._createIniSettings()

    def saveSimpleConfig(self, key, value, sync=True):
        if isinstance(value, bool):
            value = 1 if value else 0

        self._qsettings().setValue(key, value)
        if sync:
            self._qsettings().sync()

    def simpleConfigValue(self, key, defaultValue=None):
        value = self._qsettings().value(key, defaultValue)
        return variantToPyValue(value)

    def simpleConfigStrValue(self, key, defaultValue=""):
        return str(self.simpleConfigValue(key, defaultValue=defaultValue))

    def simpleConfigBoolValue(self, key, defaultValue=False):
        value = self.simpleConfigValue(key, defaultValue=defaultValue)
        if value == "0":
            value = False
        return bool(value)

    def simpleConfigIntValue(self, key, defaultValue=0):
        configValue = self.simpleConfigValue(key, defaultValue=defaultValue) or 0
        if isinstance(configValue, str):
            if not configValue.isdigit():
                return 0

        return int(configValue)

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

    def testDirSettings(self):
        with SettingsGroupContext(constants.CONFIG_KEY_SAVED_TEST_DIR) as settings:
            logger.debug("Settings ini file:%s", settings.fileName())
            names = settings.childGroups()
            data = collections.OrderedDict()
            for n in names:
                with SettingsGroupContext(n):
                    data[n] = (
                        settings.simpleConfigStrValue(
                            constants.CONFIG_KEY_TEST_TOP_DER
                        ),
                        settings.simpleConfigStrValue(
                            constants.CONFIG_KEY_TEST_START_DER
                        ),
                    )

        return data

    def __repr__(self):
        return "AppSettings({})".format(self._qsettings().fileName())
