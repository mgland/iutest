# Copyright 2019-2020 by Wenfeng Gao, MGLAND animation studio. All rights reserved.
# This file is part of IUTest, and is released under the "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import sys
import logging
from iutest import dependencies
from iutest.core import pathutils

logger = logging.getLogger(__name__)


def isReimportFeatureAvailable(silentCheck=False):
    if not hasattr(sys, "maxint"):
        return False
    if silentCheck:
        return dependencies.ReimportWrapper.get().isValid()

    return dependencies.ReimportWrapper.check()


def isModuleModified(dotPath):
    if not isReimportFeatureAvailable():
        return None
    return dependencies.ReimportWrapper.getModule().modified(dotPath)


def reimportByModulePath(dotPath):
    if not isReimportFeatureAvailable():
        return
    try:
        mod = pathutils.objectFromDotPath(dotPath)
        dependencies.ReimportWrapper.getModule().reimport(mod)
        logger.info("Reimported module: %s", dotPath)
    except:
        logger.exception("Error reloading module: %s", dotPath)


def reimportAllChangedPythonModules(inclusiveKeyword=None, exclusiveKeyword=None):
    """
    Args:
        filterKeyword (str): A keyword to 
    """
    if not isReimportFeatureAvailable():
        return

    def _iterFilteredModules(modules):
        if not modules:
            return

        for module in modules:
            if inclusiveKeyword and inclusiveKeyword.lower() not in module.lower():
                logger.debug(
                    "Ignore %s since it does not match %s", module, inclusiveKeyword
                )
                continue

            if exclusiveKeyword and exclusiveKeyword.lower() in module.lower():
                logger.debug("Ignore %s since it matches %s", module, exclusiveKeyword)
                continue

            yield module

    changed = dependencies.ReimportWrapper.getModule().modified()
    changed = list(_iterFilteredModules(changed))
    if changed:
        print("Reimporting: {} ...".format(changed))
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
