from nose2 import events
from nose2.plugins.loader import discovery

class RemoveDuplicatedTests(events.Plugin, discovery.Discoverer):
    """If the DiscoveryLoader and the EggDiscoveryLoader plugins are enabled at the same time,
    there will be duplicated tests discovered as they both call _find_tests_in_module() which
    will discover tests no matter it is egg or not.
    """
    alwaysOn = True
    configSection = 'discovery'

    def registerInSubprocess(self, event):
        event.pluginClasses.append(self.__class__)

    def _removeDuplicate(self, tests):
        uniqueTests = []
        for t in tests:
            if t not in uniqueTests:
                uniqueTests.append(t)
        return uniqueTests

    def loadTestsFromName(self, event):
        # This is where the EggDiscoveryLoader plugin introduce the duplicated plugin.
        # To-Do: Lodge the issue in nose2 repro.
        event.extraTests = self._removeDuplicate(event.extraTests )

    def loadTestsFromNames(self, event):        
        return None
