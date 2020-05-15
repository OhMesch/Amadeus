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

    def __contains__(self, animeTitleOrAlias):
        if not animeTitleOrAlias:
            return False
        if animeTitleOrAlias.lower() in self.anime_url:
            return True
        for animeTitle, alias in self.anime_alias.items():
            if animeTitleOrAlias == alias:
                return True
        return False

    def getTitleFromAlias(self, animeTitleOrAlias):
        if not animeTitleOrAlias:
            return ''
        if animeTitleOrAlias in self.anime_url:
            return self.anime_url[animeTitleOrAlias]
        for alias, animeTitle in self.anime_alias.items():
            if animeTitleOrAlias == alias:
                return animeTitle
        return ''

    def setUpLogging(self, data_dir):
        logging_dir = os.path.join(data_dir, 'logging')
        if not os.path.exists(logging_dir):
            os.makedirs(logging_dir)
        log_file = os.path.join(logging_dir, 'log_file.log')

        self.logger = logging.getLogger('my_fantastical_logger')
        
        ## handlers ##
        f_handler = RotatingFileHandler(log_file, maxBytes=20000, backupCount=3)
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)
        self.logger.addHandler(f_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)

        # self.logger.setLevel(logging.INFO)
        # self.logger.setLevel(logging.WARNING)
        # self.logger.setLevel(logging.ERROR)
        # self.logger.setLevel(logging.CRITICAL)
        self.logger.setLevel(logging.DEBUG)
        self.logger.warning('setUpLogging: Logger created')

    # TODO honestly im just using random python exceptions for control flow. ignore the names and add custom exceptions later
    def addNewAnime(self, url, alias = ''):
        if not validators.url(url):
            raise ValueError()
        if ' ' in alias:
            errMsg = 'alias provided: {0} has whitespace in it, please remove the whitespace'.format(alias)
            raise UnboundLocalError()

        animeNameClean = self.cleanAnimeName(url.split("/")[-1])
        self.addUrl(animeNameClean, url)
        self.setEpisode(animeNameClean)
        self.setSeason(animeNameClean, "1")
        self.addAlias(animeNameClean, alias)

    def cleanAnimeName(self, dirtyName):
        animeNameLower = dirtyName.replace('-',' ').lower()
        animeNameClean = " ".join(list(map(lambda x: x.capitalize(), animeNameLower.split())))
        return animeNameClean

    def stringifyAnimeInformation(self):
        joining = []
        for full_title, episode_num in self.anime_ep.items():
            season = self.anime_season[full_title]
            
            # Alias matching: TODO Uses O(N) loop to match aliases, probably need reverse dictionary
            print_alias_string = ''
            aliases = []
            for alias, curr_full_title in self.anime_alias.items():
                if curr_full_title == full_title:
                    self.logger.debug('alias found for: {0}, alias is: {1}'.format(curr_full_title, alias))
                    aliases.append('"' + alias + '"')
            if aliases:
                print_alias_string = ' Aliases: [' + ', '.join(aliases) + ']'

            # Priority matching: TODO Uses O(N) loop to match aliases, probably need reverse dictionary
            print_priority_string = ''
            priorities = []
            for priority in self.numPrioManager.getPriorities(full_title) + self.tagPrioManager.getPriorities(full_title):
                priorities.append(priority)
            if priorities:
                print_priority_string = '\n{0}Priorities: '.format(' ' * 4) + ', '.join(priorities)

            joining.append('**{1}**{2}:\n{0}Season {3} - Episode {4}{5}'.format(
                ' ' * 4, full_title, print_alias_string, str(season), str(episode_num), print_priority_string))
        return '\n'.join(joining)

    def addAlias(self, animeTitle, alias):
        #TODO remove exceptions
        if not alias:
            return False
        if ' ' in alias:
            errMsg = 'alias provided: {0} has whitespace in it, please remove the whitespace'.format(alias)
            raise UnboundLocalError()
        if animeTitle.lower() in self.anime_alias:
            self.anime_alias[alias] = self.anime_alias[animeTitle.lower()]
            return animeTitle.lower()
        elif animeTitle in self.anime_ep:
            self.anime_alias[alias] = animeTitle
            return animeTitle
        return False

    def removeAlias(self, alias):
        del self.anime_alias[alias]

    def setEpisode(self, show, episodeNumber = 1):
        self.anime_ep[show] = episodeNumber

    # TODO don't we need to remove from a ton of different storages here
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
            popOrder = self.tagPrioManager.getAnimeSequence(tag)
        else:
            popOrder = self.numPrioManager.getAnimeSequence()

        #TODO DRY -> Can we reuse getEpAndIncriment? Might have a hard time if there is nothing there.
        self.logger.debug('pop: poporder is: {0}'.format(popOrder))
        for anime in popOrder:
            currEpNum = self.getCurrEpNumber(anime)
            currEpLink = self.getEpisodeFromTitle(anime, currEpNum)
            if currEpLink:
                self.incrementStack(anime)
                return (currEpLink, currEpNum, anime)
        return (None, None, None)

    def setPrio(self, animeTitleOrAlias, key):
        animeTitle = self.getTitleFromAlias(animeTitleOrAlias)
        if not animeTitle:
            return False
        if checkers.is_integer(key):
            prioManager = self.numPrioManager
        else:
            prioManager = self.tagPrioManager
        prioManager.addPrio(animeTitleOrAlias, key)
        return True

    def removePrio(self, animeTitleOrAlias, key):
        if checkers.is_integer(key):
            prioManager = self.numPrioManager
        else:
            prioManager = self.tagPrioManager
        prioManager.removePrio(animeTitleOrAlias, key)