import logging
import os
'''
from iutest import dependencies
pytest = dependencies.PyTestWrapper.getModule()

logger = logging.Logger(__name__)

def _power(inputValue):
    return inputValue * inputValue


def test_simpleApproved():
    """ a doctest in a docstring
    >>> _power(5)
    25
    >>> _power(4)
    12
    """
    assert _power(5) == 25
    

def test_simpleFailed():
    assert _power(5) == 6


@pytest.fixture()
def _prepareSomthing(tmpdir_factory):
    return tmpdir_factory.mktemp("data").join("temp.txt")


def test_preparedTempFile(_prepareSomthing):
    print ("Prepared file:", _prepareSomthing)
    print (dir(_prepareSomthing))


def test_toSkip():
    print (_power(5))
    pytest.skip('This test just to be skipped')



# ---------------------------------------------

class TestSomething:
    def test_ok(self):
        x = "this"
        assert "h" in x

    def test_failed(self):
        x = "hello"
        assert hasattr(x, "check")

'''