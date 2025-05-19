import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest

from amadeus.DictionaryStorage import getDictionaryStorage


@pytest.fixture(scope="function")
def unique_dictionary_storage(tmpdir):
    return getDictionaryStorage("testfilename", tmpdir.strpath)


@pytest.fixture(scope="function")
def filled_unique_dictionary_storage(tmpdir):
    ds = getDictionaryStorage("testfilename", tmpdir.strpath)
    ds[11] = "fishy"
    ds["dogs"] = 1
    ds["wallet"] = [1, 2, 3]
    return ds


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
        assert unique_dictionary_storage[key] == value

    def test_get_2(self, unique_dictionary_storage):
        with pytest.raises(KeyError):
            assert unique_dictionary_storage["datathatdoesntexist"] == ""

    def test_iter(self, filled_unique_dictionary_storage):
        for i in filled_unique_dictionary_storage:
            print(i)

    # TODO
    @pytest.mark.skip("Not Implemented")
    def test_get_keys(self, unique_dictionary_storage):
        pass

    @pytest.mark.parametrize("key, value", [
        (11, "fishy"),
        (10, 7),
        (1, [1, 2, 3])
    ])
    def test_writing_reading_keys_int(self, unique_dictionary_storage, key, value):
        unique_dictionary_storage[key] = value
        assert key in unique_dictionary_storage

    @pytest.mark.parametrize("key, value", [
        ("one", "fishy"),
        ("two", 7),
        ("3", [1, 2, 3])
    ])
    def test_writing_reading_keys_string(self, unique_dictionary_storage, key, value):
        unique_dictionary_storage[key] = value
        assert key in unique_dictionary_storage

    @pytest.mark.parametrize("key, value", [
        ("one", 1),
        ("two", 2),
        ("3", 3)
    ])
    def test_writing_reading_values_int(self, unique_dictionary_storage, key, value):
        unique_dictionary_storage[key] = value
        assert unique_dictionary_storage[key] == value

    @pytest.mark.skip("Skipping because json.dumps doesnt allow tuples to be keys")
    @pytest.mark.parametrize("key, value", [
        ("one", "1"),
        (2, "cat"),
        ((2, 3), "BigBoiOnly")
    ])
    def test_writing_reading_values_string(self, unique_dictionary_storage, key, value):
        unique_dictionary_storage[key] = value
        assert unique_dictionary_storage[key] == value

    @pytest.mark.skip("Skipping because json.dumps doesnt allow tuples to be keys")
    @pytest.mark.parametrize("key, value", [
        ("one", [1, 2, 3]),
        (2, ["a", "b", "c"]),
        ((2, 3), ["BigBoiOnly", 43, (1, 2)])
    ])
    def test_writing_reading_values_list(self, unique_dictionary_storage, key, value):
        unique_dictionary_storage[key] = value
        assert unique_dictionary_storage[key] == value

    def test_get_valid_keys(self, filled_unique_dictionary_storage):
        assert filled_unique_dictionary_storage.get(11, 0) == "fishy"
        assert filled_unique_dictionary_storage.get("dogs", (1, 2, 3)) == 1
        assert filled_unique_dictionary_storage.get("wallet") == [1, 2, 3]

    def test_get_bad_keys(self, filled_unique_dictionary_storage):
        assert filled_unique_dictionary_storage.get(7, 3) == 3
        assert filled_unique_dictionary_storage.get("11", "cat") == "cat"
        assert filled_unique_dictionary_storage.get("42", [1, 5, 7]) == [1, 5, 7]
        assert filled_unique_dictionary_storage.get(3) is None
