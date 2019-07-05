import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest

from amadeus.DictionaryStorage import DictionaryStorage

@pytest.fixture(scope="function")
def unique_dictionary_storage(tmpdir):
    return DictionaryStorage("testfilename", tmpdir.strpath)

class TestDictionaryStorage():
    @pytest.mark.parametrize("key, value", [
        (10, "fish"),
        (10, 7),
        ("dogs", 4),
        ("dogs", "cats")
    ])
    def test_set(self, unique_dictionary_storage, key, value): 
        unique_dictionary_storage[key] = value

    @pytest.mark.parametrize("key, value", [
        (11, "fishy"),
        (10, 7),
        ("dogs", 4),
        ("dogs", "cats")
    ])
    def test_get_1(self, unique_dictionary_storage, key, value): 
        unique_dictionary_storage[key] = value
        assert unique_dictionary_storage[key] == str(value)

    def test_get_2(self, unique_dictionary_storage): 
        with pytest.raises(KeyError):
        	assert unique_dictionary_storage["datathatdoesntexist"] == ""