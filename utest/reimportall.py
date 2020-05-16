from utest.libs import reimport


def reimportAllChangedPythonModules():
    changed = reimport.modified()
    if changed:
        print("Reimport modules: {}".format(changed))
        reimport.reimport(*changed)
    else:
        print("No changed modules!")
    return changed
