import logging
from logging.handlers import RotatingFileHandler
import os

from amadeus.DictionaryStorage import getDictionaryStorage
from amadeus.CrunchyWebScraper import CrunchyWebScraper
from amadeus.PriorityManager import NumericPriorityManger, TagPriorityManger
from validator_collection import validators, checkers

class Amadeus():
    def __init__(self, data_dir=None):
        # Resolve data_dir 
        if not data_dir:
            data_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "data"))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.setUpLogging(data_dir)

        # Create storage objects
        self.anime_url = getDictionaryStorage("anime_url", data_dir)
        self.anime_ep = getDictionaryStorage("anime_ep", data_dir)
        self.anime_alias = getDictionaryStorage("anime_alias", data_dir)
        self.anime_season = getDictionaryStorage("anime_season", data_dir)
        self.numPrioManager = NumericPriorityManger(data_dir)
        self.tagPrioManager = TagPriorityManger(data_dir)
        self.crunchy_scraper = CrunchyWebScraper()
        self.data_dir = data_dir

    def __str__(self): # could probably return each of these better
        url_data = str(self.anime_url)
        stack_data = str(self.anime_ep)
        alias_data = str(self.anime_alias)
        season_data = str(self.anime_season)
        num_prio_data = str(self.numPrioManager)
        tag_prio_data = str(self.tagPrioManager)
        return "URL Data:\n{0}\nStack Data:\n{1}\nAlias Data:\n{2}\nSeason Data:\n{3}\nNumeric Priority Manager:\n{4}\nTag Priority Manager:\n{5}\n".format(
            url_data, stack_data, alias_data, season_data, num_prio_data, tag_prio_data)

    def setUpLogging(self, data_dir):
        logging_dir = os.path.join(data_dir, 'logging')
        if not os.path.exists(logging_dir):
            os.makedirs(logging_dir)
        log_file = os.path.join(logging_dir, 'log_file.log')

        self.logger = logging.getLogger('my_fantastical_logger')
        
        ## handlers ##
        f_handler = RotatingFileHandler(log_file, maxBytes=2000, backupCount=3)
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)
        self.logger.addHandler(f_handler)

        # self.logger.setLevel(logging.INFO)
        # self.logger.setLevel(logging.WARNING)
        # self.logger.setLevel(logging.ERROR)
        # self.logger.setLevel(logging.CRITICAL)
        self.logger.setLevel(logging.DEBUG)

        for i in range(100000):
            self.logger.warning('Logger has been created ' + str(i))

    def stringifyAnimeInformation(self):
        joining = []
        for full_title, episode_num in self.anime_ep.items():
            season = self.anime_season[full_title]
            
            # TODO Uses O(N) loop to match aliases, probably need reverse dictionary
            print_alias_string = ''
            aliases = []
            for alias, curr_full_title in self.anime_alias.items():
                if curr_full_title == full_title:
                    aliases.append('"' + alias + '"')
            if aliases:
                print_alias_string = ' [' + ', '.join(aliases) + ']'

            joining.append('{0}{1}: **Season {2} - Episode {3}**'.format(full_title, print_alias_string, str(season), str(episode_num)))
        return '\n'.join(joining)

    def addAlias(self, existing_ey, new_key):
        if existing_ey.lower() in self.anime_alias:
            self.anime_alias[new_key] = self.anime_alias[existing_ey.lower()]
            return existing_ey.lower()
        elif existing_ey in self.anime_ep:
            self.anime_alias[new_key] = existing_ey
            return existing_ey

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