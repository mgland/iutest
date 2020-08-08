import logging
logger = logging.getLogger(__name__)


class _ErrorDummy(object):
    def __getattribute__(self, name):
        return _ErrorDummy()

    def __call__(self, *_, **__):
        return _ErrorDummy()

    def __repr__(self):
        return "Error Happened."



class _ModuleWrapper(object):
    @classmethod
    def get(cls):
        return None

    @classmethod
    def reload(cls):
        cls.get()._tryImport(force=True)

    def __init__(self):
        self._mod = None
        self._tryImport(force=False)

    def _issueNotInstalledError(self):
        logger.error("The package '%s' is not installed", self.__class__.__name__)
        
    def _tryImport(self, force):
        err = "Please use derived class instead base class {}".format(self.__class__.__name__)
        raise NotImplementedError(err)

    def isValid(self):
        return bool(self._mod)
        
    def __getattribute__(self, name):
        if hasattr(_ModuleWrapper, name):
            return object.__getattribute__(self, name)

        mod = object.__getattribute__(self, "_mod")
        if not mod:
            object.__getattribute__(self, "_issueNotInstalledError")()
            return _ErrorDummy()

        return object.__getattribute__(mod, name)
    

class ReimportWrapper(_ModuleWrapper):
    _instance = None

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
        
    def _tryImport(self, force):
        if not force and self._mod:
            return
        try:
            import reimport
            self._mod = reimport
        except ImportError:
            self._issueNotInstalledError()
