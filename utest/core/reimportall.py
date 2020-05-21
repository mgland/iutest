import logging
from utest.libs import reimport

logger = logging.getLogger(__name__)

def reimportAllChangedPythonModules():
    changed = reimport.modified()
    if changed:
        print("Start reimporting the changed modules: {}".format(changed))
        for module in changed:
            try:
                reimport.reimport(module)
            except Exception:
                logger.exception('Unable to reimport module %s', module)
    else:
        print("No changed modules to reimport :)")
    return changed
