import random
from amadeus.DictionaryStorage import DictionaryStorage


class PriorityManger():
    def __init__(self, filename, data_dir=None):
        self.prio = DictionaryStorage(filename, data_dir)

    def __str__(self):
        string = ""
        for key in sorted(self.prio.keys()):
            string += str(key) + ":"
            for ep in self.prio[key]:
                string += "\n\t" + ep
            string += "\n\n"
        return string

    def addPrio(self, prioTargetName, priority):
        if priority in self.prio:
            if prioTargetName not in self.prio[priority]:
                self.prio[priority].append(prioTargetName)
        else:
            self.prio[priority] = [prioTargetName]

    def removePrio(self, prioTargetName, priority):
        if priority in self.prio and prioTargetName in self.prio[priority]:
            self.prio[priority].remove(prioTargetName)


class TagPriorityManger(PriorityManger):
    def __init__(self, data_dir=None):
        super().__init__("priotag", data_dir)

    def getTitleSequence(self, tag):
        titles = self.prio.get(tag, [])
        return random.sample(titles, len(titles))


class NumericPriorityManger(PriorityManger):
    def __init__(self, data_dir=None):
        super().__init__("prionumeric", data_dir)
        self.lookup = DictionaryStorage("reverseprionumeric", data_dir)

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
    def getTitleSequence(self):
        sortedPrioKeys = sorted(map(int, (list(self.prio.keys()))))
        weightMixedTitles = []
        for prioKey in sortedPrioKeys:
            currPrio = self.prio[prioKey]
            weightMixedTitles.extend(random.sample(currPrio, len(currPrio)))
        return weightMixedTitles
