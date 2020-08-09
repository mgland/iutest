import logging
from iutest import dependencies
from iutest.core import pathutils

logger = logging.getLogger(__name__)


def reimportByDotPath(dotPath):
    if not dependencies.ReimportWrapper.check():
        return
    try:
        mod = pathutils.objectFromDotPath(dotPath)
        dependencies.ReimportWrapper.getModule().reimport(mod)
        logger.info("Reimported module: %s", dotPath)
    except:
        logger.exception("Error reloading module: %s", dotPath)


def reimportAllChangedPythonModules():
    if not dependencies.ReimportWrapper.check():
        return

    changed = dependencies.ReimportWrapper.getModule().modified()
    if changed:
        print("Reimporting: {}".format(changed))
        successCount = 0
        failedCount = 0
        for module in changed:
            try:
                dependencies.ReimportWrapper.getModule().reimport(module)
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
