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
        unique_amadeus.addStack("SlimeLongName")
        assert unique_amadeus.stack["SlimeLongName"] == 1

    def test_add_stack_2(self, unique_amadeus): 
        with pytest.raises(Exception):
            unique_amadeus.addStack("SlimeLongName")
            unique_amadeus.addStack("SlimeLongName")

    def test_remove_stack_1(self, unique_amadeus): 
        unique_amadeus.addStack("DearPhillip")
        unique_amadeus.removeStack("DearPhillip")
        assert "DearPhillip" not in unique_amadeus.stack

    def test_remove_stack_2(self, unique_amadeus): 
        with pytest.raises(KeyError):
            unique_amadeus.removeStack("DearPhillip")

    @pytest.mark.parametrize("actual, alias", [
        ("123", "456"),
        ("SlimeLongName", "Slime")
    ])
    def test_add_alias_1(self, unique_amadeus, actual, alias):
        unique_amadeus.addStack(actual)
        unique_amadeus.addAlias(actual, alias)
        assert unique_amadeus.alias[alias] == actual

    def test_add_alias_2(self, unique_amadeus):
        unique_amadeus.addStack("SlimeLongName")
        unique_amadeus.addAlias("SlimeLongName", "Slime")
        unique_amadeus.addAlias("SlimeLongName", "AnotherSlimeAlias")
        assert unique_amadeus.alias["Slime"] == "SlimeLongName"
        assert unique_amadeus.alias["AnotherSlimeAlias"] == "SlimeLongName"

    def test_add_alias_3(self, unique_amadeus): 
        with pytest.raises(Exception):
            unique_amadeus.addAlias("SlimeLongName", "Slime")

    def test_add_alias_4(self, unique_amadeus): 
        with pytest.raises(Exception):
            unique_amadeus.addAlias("SlimeLongName", "Slime")
            unique_amadeus.addAlias("SlimeLongName", "Slime")

    def test_remove_alias_1(self, unique_amadeus):
        unique_amadeus.addStack("SlimeLongName")
        unique_amadeus.addAlias("SlimeLongName", "BigSlime")
        unique_amadeus.removeAlias("BigSlime")
        assert "BigSlime" not in unique_amadeus.alias

    def test_remove_alias_2(self, unique_amadeus): 
        with pytest.raises(KeyError):
            unique_amadeus.removeAlias("KeyThatDoesntExist")

    # integration tests
    def cleanAnimeName(self, dirtyName): 
        animeNameLower = dirtyName.replace('-',' ').lower()
        animeNameClean = " ".join(list(map(lambda x: x.capitalize(), animeNameLower.split())))
        return animeNameClean

    def test_add_anime_on_season_with_alias(self, unique_amadeus):
        jojoUrl = "https://www.crunchyroll.com/jojos-bizarre-adventure"
        animeNameClean = self.cleanAnimeName(jojoUrl.split("/")[-1])
        unique_amadeus.addUrl(animeNameClean, jojoUrl)
        unique_amadeus.addStack(animeNameClean)
        unique_amadeus.setSeason(animeNameClean, "2")
        unique_amadeus.addAlias(animeNameClean, "jojo")

        trueTitle = unique_amadeus.getTitleFromKey("jojo")
        assert trueTitle == "Jojos Bizarre Adventure"
        # assert CrunchyWebScraper.getEpisodeLink(unique_amadeus.url[trueTitle], "1", unique_amadeus.season[trueTitle])
