import logging
from utest.libs import reimport

logger = logging.getLogger(__name__)


def reimportAllChangedPythonModules():
    changed = reimport.modified()
    if changed:
        print("Reimporting: {}".format(changed))
        successCount = 0
        failedCount = 0
        for module in changed:
            try:
                reimport.reimport(module)
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
