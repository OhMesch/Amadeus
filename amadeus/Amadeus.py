from amadeus.DictionaryStorage import DictionaryStorage
from amadeus.CrunchyWebScraper import CrunchyWebScraper

class Amadeus():
    def __init__(self, data_dir = None):
        self.url = DictionaryStorage("url", data_dir)
        self.stack = DictionaryStorage("stack", data_dir)
        self.alias = DictionaryStorage("alias", data_dir)
        self.season = DictionaryStorage("season", data_dir)
        self.crunchy_scraper = CrunchyWebScraper()

    def __str__(self): # could probably return each of these better
        url_data = str(self.url)
        stack_data = str(self.stack)
        alias_data = str(self.alias)
        season_data = str(self.season)
        return "URL Data:\n{0}\nStack Data:\n{1}\nAlias Data:\n{2}\nSeason Data:\n{3}\n".format(
            url_data, stack_data, alias_data, season_data)

    def addAlias(self, existing_ey, new_key):
        if existing_ey in self.alias:
            self.alias[new_key] = self.alias[existing_ey]
        elif existing_ey in self.stack:
            self.alias[new_key] = existing_ey
        else:
            raise Exception("Alias must correspond to a show on the stack or an previously aliased name.")

    def removeAlias(self, alias):
        del self.alias[alias]

    def addStack(self, show):
        if show in self.stack:
            raise Exception("{0} already is in self.stack".format(show))
        self.stack[show] = 1

    def setStack(self, show, ep):
        self.stack[show] = ep

    def removeStack(self, show):
        del self.stack[show]

    def getEpisodeFromTitle(self, trueTitle, episode):
        return self.crunchy_scraper.getEpisodeLink(self.getUrlFromTitle(trueTitle), 
            episode, self.season[trueTitle])

    def getUrlFromTitle(self, trueTitle):
        return self.url[trueTitle]

    def addUrl(self, anime, url):
        self.url[anime] = url

    def getTitleFromKey(self, key):
        if key in self.stack:
            return key
        if key in self.alias:
            return self.alias[key]

    def getCurrEpNumber(self, anime):
        return self.stack[anime]

    def incrementStack(self, anime):
        self.stack[anime] = str(int(self.stack[anime]) + 1) # should just store as number??

    def setSeason(self, anime, season):
        self.season[anime] = season