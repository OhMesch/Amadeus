import sys
import os.path
import pickle
import json
import logging

# todo Add ability for multiple data stores (e.g. john_tom, john_kyle)
def getDictionaryStorage(filename, data_dir):
    return JSONDictionaryStorage(filename, data_dir)
    # return PickleDictionaryStorage(filename, data_dir)


class DictionaryStorage:
    def __init__(self, filename, data_dir, file_extension):
        # Logging
        self.logger = logging.getLogger('my_fantastical_logger')
        self.logger.warning('__init__: {0} has been created'.format(self.__class__.__name__))

        # Other
        self.data = dict()
        self.data_filepath = os.path.join(data_dir, filename + '.' + file_extension)

        if os.path.exists(self.data_filepath):
            self.loadFromStorage()
        

    def __str__(self):
        string = "{\n"
        for k, v in self.data.items():
            string += "\t{0}: {1}\n".format(k, v)
        string += "}"
        return string

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return bool(key in self.data)

    def __setitem__(self, key, value):
        self.data[key] = value
        self.writeToStorage()

    def __iter__(self):
        return iter(self.data.keys())

    def __delitem__(self, key):
        char_key = str(key)
        del self.data[char_key]
        self.writeToStorage()

    def get(self, key, defaultVal=None):
        return self.data.get(key, defaultVal)

    def items(self):
        for key in self:
            yield (key, self[key])

    def keys(self):
        return self.data.keys()

    def writeToStorage(self):
        raise Exception('This is the base class! Cannot call writeToStorage')

class JSONDictionaryStorage(DictionaryStorage):
    def __init__(self, filename, data_dir):
        super().__init__(filename, data_dir, 'json')

    def loadFromStorage(self):
        self.logger.warning('loadFromStorage: loading file: {0} as JSON'.format(self.data_filepath))
        with open(self.data_filepath) as fd:
            self.data = json.load(fd)

    def writeToStorage(self):
        self.logger.warning('writeToStorage: writing to file: {0} as JSON'.format(self.data_filepath))
        with open(self.data_filepath, 'w') as fd:
            json.dump(self.data, fd)

class PickleDictionaryStorage(DictionaryStorage):
    def __init__(self, filename, data_dir):
        super().__init__(filename, data_dir, 'pickle')

    def loadFromStorage(self):
        self.logger.warning('loadFromStorage: reading from file: {0} as PICKLE binary'.format(self.data_filepath))
        with open(self.data_filepath, "rb") as fileIO:
            self.data = pickle.load(fileIO)

    def writeToStorage(self):
        self.logger.warning('writeToStorage: writing to file: {0} as PICKLE binary'.format(self.data_filepath))
        with open(self.data_filepath, "wb") as fileIO:
            pickle.dump(self.data, fileIO)
