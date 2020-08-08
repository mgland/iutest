import logging
from iutest import dependencies
from iutest.core import pathutils

logger = logging.getLogger(__name__)


def reimportByDotPath(dotPath):
    try:
        mod = pathutils.objectFromDotPath(dotPath)
        dependencies.ReimportWrapper.get().reimport(mod)
        logger.info("Reimported module: %s", dotPath)
    except:
        logger.exception("Error reloading module: %s", dotPath)


def reimportAllChangedPythonModules():
    changed = dependencies.ReimportWrapper.get().modified()
    if changed:
        print("Reimporting: {}".format(changed))
        successCount = 0
        failedCount = 0
        for module in changed:
            try:
                dependencies.ReimportWrapper.get().reimport(module)
            except Exception:
                logger.exception("Unable to reimport module %s", module)
                failedCount += 1
            else:
                successCount += 1
        if not failedCount:
            print("{} modules reimported.".format(successCount))
        else:
            if not successCount:
                print("All {} modules failed to reimport.".format(failedCount))
            else:
                print(
                    "{} modules reimported, {} modules failed to reimport.".format(
                        successCount, failedCount
                    )
                )

    else:
        print("No modules need to reimport :)")
    return changed
