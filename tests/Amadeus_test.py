import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from amadeus.Amadeus import Amadeus
from amadeus.CrunchyWebScraper import CrunchyWebScraper


# see: https://docs.pytest.org/en/latest/builtin.html#builtinfixtures
# for explanation on tmpdir

# run once at begining of module
# def setup_module(module):
#     """..."""

# run at end of module
# def teardown_module(module):
#     """..."""

@pytest.fixture(scope="function")
def unique_amadeus(tmpdir):
    return Amadeus(tmpdir.strpath)

class TestAmadeus():
    def test_add_stack_1(self, unique_amadeus): 
        unique_amadeus.addNewAnimeNoUrl("Slime Long Name")
        assert unique_amadeus.anime_ep["Slime Long Name"] == 1

    def test_remove_stack_1(self, unique_amadeus): 
        unique_amadeus.addNewAnimeNoUrl("Dear Phillip")
        unique_amadeus.removeAnime("Dear Phillip")
        assert "Dear Phillip" not in unique_amadeus.anime_ep

    def test_remove_stack_2(self, unique_amadeus): 
        assert False == unique_amadeus.removeAnime("Dear Phillip")

    @pytest.mark.parametrize("actual, alias", [
        ("123", "456"),
        ("Slime Long Name", "Slime")
    ])
    def test_add_alias_1(self, unique_amadeus, actual, alias):
        unique_amadeus.addNewAnimeNoUrl(actual)
        unique_amadeus.addAlias(actual, alias)
        assert unique_amadeus.anime_alias[alias] == actual

    def test_add_alias_2(self, unique_amadeus):
        unique_amadeus.addNewAnimeNoUrl("Slime Long Name")
        unique_amadeus.addAlias("Slime Long Name", "Slime")
        unique_amadeus.addAlias("Slime Long Name", "slimealias")
        assert unique_amadeus.anime_alias["Slime"] == "Slime Long Name"
        assert unique_amadeus.anime_alias["slimealias"] == "Slime Long Name"

    def test_add_alias_3(self, unique_amadeus): 
        assert False == unique_amadeus.addAlias("Slime Long Name", "Slime")

    def test_add_alias_4(self, unique_amadeus): 
        unique_amadeus.addAlias("Slime Long Name", "Slime")
        assert False == unique_amadeus.addAlias("Slime Long Name", "Slime")

    def test_remove_alias_1(self, unique_amadeus):
        unique_amadeus.addNewAnimeNoUrl("Slime Long Name")
        unique_amadeus.addAlias("Slime Long Name", "BiggestSlime")
        unique_amadeus.removeAlias("BiggestSlime")
        assert "BiggestSlime" not in unique_amadeus.anime_alias

    def test_remove_alias_2(self, unique_amadeus): 
        assert False == unique_amadeus.removeAlias("KeyThatDoesntExist")

    # integration tests
    def cleanAnimeName(self, dirtyName): 
        animeNameLower = dirtyName.replace('-',' ').lower()
        animeNameClean = " ".join(list(map(lambda x: x.capitalize(), animeNameLower.split())))
        return animeNameClean

    def test_add_anime_on_season_with_alias(self, unique_amadeus):
        jojoUrl = "https://www.crunchyroll.com/jojos-bizarre-adventure"
        unique_amadeus.addNewAnime(jojoUrl, 1, 2, "jojo")
        
        trueTitle = unique_amadeus.getTitleFromAlias("jojo")
        assert trueTitle == "Jojos Bizarre Adventure"
        # assert CrunchyWebScraper.getEpisodeLink(unique_amadeus.url[trueTitle], "1", unique_amadeus.season[trueTitle])
