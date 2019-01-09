import sys
import os.path
import json

class jsonDict():
	def __init__(self, jsonFileName):
		self.data = dict()
		jsonDir = sys.path[0]+"\\..\\json\\"
		self.jsonFileName = jsonDir+jsonFileName

		if not os.path.exists(jsonDir):
			os.makedirs(jsonDir)

		if os.path.exists(jsonDir+jsonFileName + ".json"):
			self.loadJ()

	def __str__(self):
		string = "{\n"
		for k,v in self.data.items():
			string += "\t{0}: {1}\n".format(k,v)
		string += "}"
		return(string)

	def __getitem__(self, key):
		return(self.data[str(key)])

	def __setitem__(self, key, value):
		self.data[str(key)] = str(value)
		self.writeJ()

	def __delitem__(self, key):
		charKey = str(key)
		if charKey in self.data: del self.data[charKey]
		self.writeJ()

	def __contains__(self, key):
		return(bool(key in self.data))

	def loadJ(self):
		with open(self.jsonFileName+".json","r") as fileIO:
			self.data = json.load(fileIO)

	def writeJ(self):
		with open(self.jsonFileName+".json","w") as fileIO:
			json.dump(self.data,fileIO)