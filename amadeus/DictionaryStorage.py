import sys
import os.path
import pickle

#todo Add ability for multiple data stores (e.g. john_tom, john_kyle)
class DictionaryStorage():
    def __init__(self, filename, data_dir = None):
        self.data = dict()
        if not data_dir:
            data_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "data"))
        self.data_filepath = os.path.join(data_dir, filename + ".p")

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        if os.path.exists(self.data_filepath):
            self.loadSerial()

    def __str__(self):
        string = "{\n"
        for k, v in self.data.items():
            string += "\t{0}: {1}\n".format(k, v)
        string += "}"
        return string

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.writeSerial()

    def __iter__(self):
        return iter(list(self.data.keys()))

    def __delitem__(self, key):
        char_key = str(key)
        del self.data[char_key]
        self.writeSerial()

    def __contains__(self, key):
        return bool(key in self.data) 

    def loadSerial(self):
        with open(self.data_filepath, "rb") as fileIO:
            self.data = pickle.load(fileIO)

    def writeSerial(self):
        with open(self.data_filepath, "wb") as fileIO:
            pickle.dump(self.data, fileIO)

    def keys(self):
        return(self.data.keys())