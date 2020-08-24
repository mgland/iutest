class TestsDuplicationRemovalHooks(object):
    """ Remove potentially duplicated tests collected.

    Notes:
        If the DiscoveryLoader and the EggDiscoveryLoader plugins are enabled at the same time,
        there will be duplicated tests discovered as they both call _find_tests_in_module() which
        will discover tests no matter it is egg or not.

        Since Nose2 uses alphabetical order or plugin module paths to decide which plugin
        to load first but to remove duplicated test we need to ensure the plugin comes after
        other discovery plugin. Thus we need to use hooks instead of plugin.
    """

    def _removeDuplicate(self, tests):
        uniqueTests = []
        for t in tests:
            if t not in uniqueTests:
                uniqueTests.append(t)
        return uniqueTests

    def loadTestsFromName(self, event):
        """Load tests from module named by event.name.
        Notes:
            This is where the EggDiscoveryLoader plugin introduce the duplicated plugin.
        """
        event.extraTests = self._removeDuplicate(event.extraTests)

    @classmethod
    def getHooks(cls):
        hook = cls()
        return [("loadTestsFromName", hook)]
