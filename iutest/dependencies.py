import logging

logger = logging.getLogger(__name__)


class _ErrorDummy(object):
    def __getattribute__(self, name):
        return _ErrorDummy()

    def __call__(self, *_, **__):
        return _ErrorDummy()

    def __repr__(self):
        return "Error Happened."

    def __iter__(self):
        yield _ErrorDummy()

    def __getitem__(self, index):
        return _ErrorDummy()

    def __bool__(self):
        return False

    def __nonzero__(self):
        return False


class _DependencyWrapper(object):
    @classmethod
    def get(cls, silent=False):
        """Get an instance of the wrapper object.

        Args:
            silent (bool): Whether we issue errors or debug when the dependency 
                is not installed.
        """
        if not hasattr(cls, "_instance"):
            return None

        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def getModule(cls, silent=False):
        wrapper = cls.get(silent=silent)
        return wrapper._mod if wrapper._mod else _ErrorDummy()

    @classmethod
    def reload(cls, silent=True):
        """Try reimport the dependency module.

        Args:
            silent (bool): Whether we issue errors or debug when the dependency 
                is not installed.
        """
        cls.get()._tryImport(force=True, silent=silent)

    def __init__(self):
        self._mod = None
        self._tryImport(force=False, silent=True)

    @classmethod
    def _issueNotInstalledError(cls, silent=True):
        if not silent:
            logger.error("The package '%s' is not installed", cls.name())
        else:
            logger.debug("The package '%s' is not installed", cls.name())

    @classmethod
    def _issueNotImplementedError(cls):
        err = "Please use a derived class instead of base class {}".format(cls.__name__)
        raise NotImplementedError(err)

    def _tryImport(self, force, silent):
        self._issueNotImplementedError()

    @classmethod
    def name(cls):
        cls._issueNotImplementedError()

    def isValid(self):
        return bool(self._mod)

    @classmethod
    def check(cls):
        if not cls.get().isValid():
            cls._issueNotInstalledError(silent=False)
            return False
        return True


class ReimportWrapper(_DependencyWrapper):
    _instance = None

    @classmethod
    def name(cls):
        return "reimport"

    def _tryImport(self, force, silent):
        if not force and self._mod:
            return
        self._mod = None
        try:
            import reimport

            self._mod = reimport
        except ImportError:
            self._issueNotInstalledError(silent)


class Nose2Wrapper(_DependencyWrapper):
    _instance = None

    @classmethod
    def name(cls):
        return "nose2"

    def _tryImport(self, force, silent):
        if not force and self._mod:
            return
        self._mod = None
        try:
            import nose2

            self._mod = nose2
        except ImportError:
            self._issueNotInstalledError(silent)


class PyTestWrapper(_DependencyWrapper):
    _instance = None

    @classmethod
    def name(cls):
        return "pytest"

    def _tryImport(self, force, silent):
        if not force and self._mod:
            return
        self._mod = None
        try:
            import pytest

            self._mod = pytest
        except ImportError:
            self._issueNotInstalledError(silent)
