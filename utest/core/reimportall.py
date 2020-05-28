import logging
from utest.libs import reimport

logger = logging.getLogger(__name__)


def reimportAllChangedPythonModules():
    changed = reimport.modified()
    if changed:
        print("Reimporting: {}".format(changed))
        for module in changed:
            try:
                reimport.reimport(module)
            except Exception:
                logger.exception("Unable to reimport module %s", module)
        print ("{} modules reimported.".format(len(changed)))
    else:
        print("No changed modules to reimport :)")
    return changed
