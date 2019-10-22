import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from amadeus.Amadeus import Amadeus
from amadeus.PriorityManager import NumericPriorityManger, TagPriorityManger


@pytest.fixture(scope="function")
def unique_amadeus(tmpdir):
    return Amadeus(tmpdir.strpath)

@pytest.fixture(scope="function")
def unique_numeric_priority_manager(tmpdir):
    prioManager = NumericPriorityManger(tmpdir.strpath)
    prioManager.addPrio("Kageyama", 1)
    prioManager.addPrio("AOT", 2)
    prioManager.addPrio("Papa Bones", 5)
    prioManager.addPrio("Kings Game", 1000)
    prioManager.addPrio("Dodododoro", 8)
    return prioManager

@pytest.fixture(scope="function")
def unique_light_numeric_priority_manager(tmpdir):
    prioManager = NumericPriorityManger(tmpdir.strpath)
    prioManager.addPrio("Kings Game", 100)
    prioManager.addPrio("AOT", 2)
    prioManager.addPrio("Papa Bones", 5)
    return prioManager

@pytest.fixture(scope="function")
def unique_numeric_priority_manager_multiple_per_prio(tmpdir):
    prioManager = NumericPriorityManger(tmpdir.strpath)
    prioManager.addPrio("Kageyama", 1)
    prioManager.addPrio("AOT", 1)
    prioManager.addPrio("Papa Bones", 1)
    prioManager.addPrio("Kings Game", 1000)
    prioManager.addPrio("Other Trash", 1000)
    prioManager.addPrio("Dodododoro", 4)
    prioManager.addPrio("Bunny", 4)
    prioManager.addPrio("Goblin", 4)
    prioManager.addPrio("Slime",3)
    return prioManager

@pytest.fixture(scope="function")
def unique_tag_priority_manager_multiple_per_prio(tmpdir):
    tagManager = TagPriorityManger(tmpdir.strpath)
    tagManager.addPrio("Kageyama", "sol")
    tagManager.addPrio("AOT", "action")
    tagManager.addPrio("Papa Bones", "isekai")
    tagManager.addPrio("Dodododoro", "action")
    tagManager.addPrio("bunny", "sol")
    tagManager.addPrio("Arrietta", "isekai")
    tagManager.addPrio("Konosuba", "isekai")
    tagManager.addPrio("Shield", "isekai")
    tagManager.addPrio("Slime", "isekai")
    return tagManager


class TestNumericPriorityManager():
    @pytest.mark.repeat(3)
    def test_unique_getAnimeSequence_returns_weighted_order(self, unique_numeric_priority_manager):
        weight_sorted_titles = unique_numeric_priority_manager.getAnimeSequence()
        assert weight_sorted_titles == ["Kageyama", "AOT", "Papa Bones", "Dodododoro", "Kings Game"]

    @pytest.mark.repeat(3)
    def test_multiple_getAnimeSequence_returns_weighted_order(self, unique_numeric_priority_manager_multiple_per_prio):
        weight_sorted_titles_rand_order = unique_numeric_priority_manager_multiple_per_prio.getAnimeSequence()
        prio1 = weight_sorted_titles_rand_order[:3]
        prio3 = weight_sorted_titles_rand_order[3]
        prio4 = weight_sorted_titles_rand_order[4:7]
        prio1000 = weight_sorted_titles_rand_order[7:]
        assert sorted(prio1) == sorted(["Kageyama", "AOT", "Papa Bones"])
        assert prio3 == "Slime"
        assert sorted(prio4) == sorted(["Bunny", "Goblin", "Dodododoro"])
        assert sorted(prio1000) == sorted(["Kings Game", "Other Trash"])

    #This dataset has about a 1/72 (1.38%) chance to return the same list twice in a row
    def test_multiple_getAnimeSequence_returns_semi_rand(self, unique_numeric_priority_manager_multiple_per_prio):
        twiceCounter = 0
        for i in range(1000):
            rand1 = unique_numeric_priority_manager_multiple_per_prio.getAnimeSequence()
            rand2 = unique_numeric_priority_manager_multiple_per_prio.getAnimeSequence()
            if rand1 == rand2:
                twiceCounter += 1
        assert twiceCounter <= 30

    def test_add_multiple_of_same_title_updates_lookup_and_order(self, unique_light_numeric_priority_manager):
        assert unique_light_numeric_priority_manager.lookup["Papa Bones"] == 5
        assert unique_light_numeric_priority_manager.getAnimeSequence() == ["AOT", "Papa Bones", "Kings Game"]

        unique_light_numeric_priority_manager.addPrio("Papa Bones", 1)
        assert unique_light_numeric_priority_manager.lookup["Papa Bones"] == 1
        assert unique_light_numeric_priority_manager.getAnimeSequence() == ["Papa Bones", "AOT", "Kings Game"]

        unique_light_numeric_priority_manager.addPrio("Papa Bones", 2000)
        assert unique_light_numeric_priority_manager.lookup["Papa Bones"] == 2000
        assert unique_light_numeric_priority_manager.getAnimeSequence() == ["AOT", "Kings Game", "Papa Bones"]

    def test_remove_prio(self, unique_light_numeric_priority_manager):
        assert unique_light_numeric_priority_manager.getAnimeSequence() == ["AOT", "Papa Bones", "Kings Game"]

        unique_light_numeric_priority_manager.removePrio("AOT")
        assert unique_light_numeric_priority_manager.getAnimeSequence() == ["Papa Bones", "Kings Game"]

        unique_light_numeric_priority_manager.removePrio("Papa Bones")
        assert unique_light_numeric_priority_manager.getAnimeSequence() == ["Kings Game"]

        unique_light_numeric_priority_manager.removePrio("Nonexistant Entry")

class TestTagPriorityManager():
    def test_unique_getAnimeSequence_returns(self, unique_tag_priority_manager_multiple_per_prio):
        solTitles = unique_tag_priority_manager_multiple_per_prio.getAnimeSequence("sol")
        assert sorted(solTitles) == sorted(["Kageyama", "bunny"])

        actionTitles = unique_tag_priority_manager_multiple_per_prio.getAnimeSequence("action")
        assert sorted(actionTitles) == sorted(["AOT", "Dodododoro"])

        isekaiTitles = unique_tag_priority_manager_multiple_per_prio.getAnimeSequence("isekai")
        assert sorted(isekaiTitles) == sorted(["Papa Bones", "Arrietta", "Konosuba", "Shield", "Slime"])

    # TODO: Need to convert more tests to using this instead of the default random provider
    def test_multiple_getAnimeSequence(self, unique_tag_priority_manager_multiple_per_prio):
        unique_tag_priority_manager_multiple_per_prio.order_of_equal_list_provider = lambda x: sorted(x)
        assert unique_tag_priority_manager_multiple_per_prio.getAnimeSequence("isekai") == ["Arrietta", "Konosuba", "Papa Bones", "Shield", "Slime"]
        unique_tag_priority_manager_multiple_per_prio.order_of_equal_list_provider = lambda x: sorted(x, reverse=True)
        assert unique_tag_priority_manager_multiple_per_prio.getAnimeSequence("isekai") == list(reversed(["Arrietta", "Konosuba", "Papa Bones", "Shield", "Slime"]))

    def test_remove_prio(self, unique_tag_priority_manager_multiple_per_prio):
        unique_tag_priority_manager_multiple_per_prio.removePrio("bunny", "sol")
        assert unique_tag_priority_manager_multiple_per_prio.getAnimeSequence("sol") == ["Kageyama"]

        unique_tag_priority_manager_multiple_per_prio.removePrio("AOT", "action")
        unique_tag_priority_manager_multiple_per_prio.removePrio("Dodododoro", "action")
        assert unique_tag_priority_manager_multiple_per_prio.getAnimeSequence("action") == []

        unique_tag_priority_manager_multiple_per_prio.removePrio("Nonexistant Entry", "isekai")
        unique_tag_priority_manager_multiple_per_prio.removePrio("Any Anime", "Nonexistant tag")
        isekaiTitles = unique_tag_priority_manager_multiple_per_prio.getAnimeSequence("isekai")
        assert sorted(isekaiTitles) == sorted(["Papa Bones", "Arrietta", "Konosuba", "Shield", "Slime"])

