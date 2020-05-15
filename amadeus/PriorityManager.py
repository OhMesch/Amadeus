import random
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
        for priority, animeTitle in self.prio.items():
            if animeTitle == wantedAnimeTitle:
                prios += priority
        return prios

    def addPrio(self, prioTargetName, priority):
        if priority not in self.prio:
            self.prio[priority] = []
        if prioTargetName not in self.prio[priority]:
            self.prio[priority].append(prioTargetName)
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

    # TODO Would a list comprehension / mapping be better here?
    def getAnimeSequence(self):
        sorted_prio_keys = sorted(map(int, (list(self.prio.keys()))))
        anime_order = []
        for key in sorted_prio_keys:
            animes = self.prio[key]
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