from amadeus.DictionaryStorage import DictionaryStorage
from amadeus.CrunchyWebScraper import CrunchyWebScraper
from amadeus.PriorityManager import NumericPriorityManger, TagPriorityManger
from validator_collection import validators, checkers

class Amadeus():
    def __init__(self, data_dir=None):
        self.anime_url = DictionaryStorage("anime_url", data_dir)
        self.anime_ep = DictionaryStorage("anime_ep", data_dir)
        self.anime_alias = DictionaryStorage("anime_alias", data_dir)
        self.anime_season = DictionaryStorage("anime_season", data_dir)
        self.numPrioManager = NumericPriorityManger(data_dir)
        self.tagPrioManager = TagPriorityManger(data_dir)
        self.crunchy_scraper = CrunchyWebScraper()

    def __str__(self): # could probably return each of these better
        url_data = str(self.anime_url)
        stack_data = str(self.anime_ep)
        alias_data = str(self.anime_alias)
        season_data = str(self.anime_season)
        num_prio_data = str(self.numPrioManager)
        tag_prio_data = str(self.tagPrioManager)
        return "URL Data:\n{0}\nStack Data:\n{1}\nAlias Data:\n{2}\nSeason Data:\n{3}\nNumeric Priority Manager:\n{4}\nTag Priority Manager:\n{5}\n".format(
            url_data, stack_data, alias_data, season_data, num_prio_data, tag_prio_data)

    def addAlias(self, existing_ey, new_key):
        if existing_ey.lower() in self.anime_alias:
            self.anime_alias[new_key] = self.anime_alias[existing_ey.lower()]
            return existing_ey.lower()
        elif existing_ey in self.anime_ep:
            self.anime_alias[new_key] = existing_ey
            return existing_ey
        return None

    def removeAlias(self, alias):
        del self.anime_alias[alias]

    def addAnime(self, show):
        if show in self.anime_ep:
            raise Exception("{0} already is in self.anime_ep".format(show))
        self.anime_ep[show] = 1

    def setEp(self, show, ep):
        self.anime_ep[show] = ep

    def removeAnime(self, show):
        del self.anime_ep[show]

    def getEpisodeFromTitle(self, trueTitle, episode):
        return self.crunchy_scraper.getEpisodeLink(self.getUrlFromTitle(trueTitle), episode, self.anime_season[trueTitle])
    
    def getSeasonEpisodeFromTitle(self, trueTitle, episode, season):
        return self.crunchy_scraper.getEpisodeLink(self.getUrlFromTitle(trueTitle), episode, season)

    def getUrlFromTitle(self, trueTitle):
        return self.anime_url[trueTitle]

    def addUrl(self, anime, url):
        self.anime_url[anime] = url

    def getTitleFromKey(self, key):
        if key in self.anime_ep:
            return key
        if key in self.anime_alias:
            return self.anime_alias[key]
        return None

    def getCurrEpNumber(self, anime):
        return self.anime_ep[anime]

    def getCurrSeasonNumber(self, anime):
        return self.anime_season[anime]

    def incrementStack(self, anime):
        self.anime_ep[anime] = str(int(self.anime_ep[anime]) + 1) #TODO should just store as number??

    def setSeason(self, anime, season):
        self.anime_season[anime] = season

    #TODO this can be clearer
    def pop(self, tag=''):
        if checkers.is_string(tag, minimum_length=1):
            popOrder = self.tagPrioManager.getTitleSequence(tag)
        else:
            popOrder = self.numPrioManager.getTitleSequence()

        #TODO DRY -> Can we reuse getEpAndIncriment? Might have a hard time if there is nothing there.
        print(popOrder)
        for anime in popOrder:
            currEpNum = self.getCurrEpNumber(anime)
            currEpLink = self.getEpisodeFromTitle(anime, currEpNum)
            if currEpLink:
                self.incrementStack(anime)
                return (currEpLink,currEpNum,anime)
        return None

    def setPrio(self, anime, key):
        if checkers.is_integer(key):
            prioManager = self.numPrioManager
        else:
            prioManager = self.tagPrioManager
        prioManager.addPrio(anime, key)

    def removePrio(self, anime, key):
        if checkers.is_integer(key):
            prioManager = self.numPrioManager
        else:
            prioManager = self.tagPrioManager
        prioManager.removePrio(anime, key)