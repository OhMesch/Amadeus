﻿import random
from amadeus.DictionaryStorage import getDictionaryStorage
import logging

class PriorityManger():
    def __init__(self, filename, data_dir):
        # Logging
        self.logger = logging.getLogger('my_fantastical_logger')
        self.logger.warning('__init__: {0} has been created'.format(self.__class__.__name__))

        # Other
        self.prio = getDictionaryStorage(filename, data_dir)
        self.order_of_equal_list_provider = lambda list_in: random.sample(list_in, len(list_in))

    def __str__(self):
        string = ""
        for key in sorted(self.prio.keys()):
            string += str(key) + ":"
            for ep in self.prio[key]:
                string += "\n\t" + ep
            string += "\n\n"
        return string

    def getPriorities(self, wantedAnimeTitle):
        prios = []
        for priority, animeTitles in self.prio.items():
            if wantedAnimeTitle in animeTitles:
                prios.append(priority)
        return prios

    def addPrio(self, prioTargetName, priority):
        success = self.prio.addToList(priority, prioTargetName)
        if success:
            self.logger.info('addPrio: for anime: {0} add priority: {1}'.format(prioTargetName, priority))

    def removePrio(self, prioTargetName, priority):
        if priority in self.prio and prioTargetName in self.prio[priority]:
            self.prio[priority].remove(prioTargetName)
            self.logger.info('removePrio: for anime: {0} remove priority: {1}'.format(prioTargetName, priority))
        else:
            self.logger.info('removePrio: for anime: {0} remove priority: {1}'.format(prioTargetName, priority))


class TagPriorityManger(PriorityManger):
    def __init__(self, data_dir):
        super().__init__("priotag", data_dir)

    def getAnimeSequence(self, tag):
        animes = self.prio.get(tag, [])
        return self.order_of_equal_list_provider(animes)

    def __str__(self):
        return super().__str__()

class NumericPriorityManger(PriorityManger):
    def __init__(self, data_dir):
        super().__init__("prionumeric", data_dir)
        self.lookup = getDictionaryStorage("reverseprionumeric", data_dir)

    def addPrio(self, prioTargetName, priority):
        if prioTargetName in self.lookup:
            super().removePrio(prioTargetName, self.lookup[prioTargetName])
        super().addPrio(prioTargetName, priority)
        self.lookup[prioTargetName] = priority

    def removePrio(self, prioTargetName):
        if prioTargetName in self.lookup:
            super().removePrio(prioTargetName, self.lookup[prioTargetName])
            del self.lookup[prioTargetName]

    def getPriorities(self, wantedAnimeTitle):
        if wantedAnimeTitle not in self.lookup:
            return []
        return [self.lookup[wantedAnimeTitle]]

    # TODO leetcode spagetti
    def getAnimeSequence(self, avaliable_titles = []):
        defaultPriority = 100

        ## asigning prio to animes without a priority explicitly set
        used = set()
        for key in self.prio.keys():
            animes = self.prio[key]
            used = used.union(set(animes)) # TODO dont make O(N) operation here
        unset_titles = list(set(avaliable_titles).difference(used))
        allPrioritiesWithAnime = list(set(self.prio.keys()).union([defaultPriority]))

        ## Iterating through priorities in order and returning a random order
        sorted_prio_keys = sorted(map(lambda x: (int(x), x), (allPrioritiesWithAnime)))
        anime_order = []
        for int_key, orig_key in sorted_prio_keys:
            animes = []
            if orig_key in self.prio:
                animes += self.prio[orig_key]
            if int_key == defaultPriority:
                animes += unset_titles
            self.logger.debug('getAnimeSequence: Numeric PriorityManager, priority: {0}, animes: {1}'.format(int_key, animes))
            anime_order.extend(self.order_of_equal_list_provider(animes))
        return anime_order
    
    def __str__(self):
        return super().__str__()

    # def getAnimeSequencePairs(self):
    #     sorted_prio_keys = sorted(map(int, (list(self.prio.keys()))))
    #     anime_order = []
    #     for key in sorted_prio_keys:
    #         animes = self.prio[key]
    #         anime_order.append((key, self.order_of_equal_list_provider(animes)))
    #     return anime_order