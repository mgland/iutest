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



class _DependencyWrapper(object):
    @classmethod
    def get(cls):
        if not hasattr(cls, "_instance"):
            return None

        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reload(cls):
        cls.get()._tryImport(force=True)

    def __init__(self):
        self._mod = None
        self._tryImport(force=False)

    def _issueNotInstalledError(self):
        logger.error("The package '%s' is not installed", self.name())

    @classmethod
    def _issueNotImplementedError(cls):
        err = "Please use derived class instead base class {}".format(cls.__name__)
        raise NotImplementedError(err)
        
    def _tryImport(self, force):
        self._issueNotImplementedError()

    @classmethod
    def name(cls):
        cls._issueNotImplementedError()

    def isValid(self):
        return bool(self._mod)
        
    def __getattribute__(self, name):
        if hasattr(_DependencyWrapper, name):
            return object.__getattribute__(self, name)

        mod = object.__getattribute__(self, "_mod")
        if not mod:
            object.__getattribute__(self, "_issueNotInstalledError")()
            return _ErrorDummy()

        return object.__getattribute__(mod, name)
    

class ReimportWrapper(_DependencyWrapper):
    _instance = None

    @classmethod
    def name(cls):
        return "reimport"

    def _tryImport(self, force):
        if not force and self._mod:
            return
        try:
            import reimport
            self._mod = reimport
        except ImportError:
            self._issueNotInstalledError()


class Nose2Wrapper(_DependencyWrapper):
    _instance = None

    @classmethod
    def name(cls):
        return "nose2"

    def _tryImport(self, force):
        if not force and self._mod:
            return
        try:
            import nose2
            self._mod = nose2
        except ImportError:
            self._issueNotInstalledError()
