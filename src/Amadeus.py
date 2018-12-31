from jsonDict import jsonDict

class Amadeus():
	def __init__(self):
		self.url = jsonDict("url")
		self.stack = jsonDict("stack")
		self.alias = jsonDict("alias")

	def __str__(self):
		urlData = str(self.url)
		stackData = str(self.stack)
		aliasData = str(self.alias)
		return("URL Data:\n{0}\nStack Data:\n{1}\nAlias Data:\n{2}\n".format(urlData, stackData, aliasData))

	def addAlias(self, existingKey, newKey):
		if existingKey in self.alias:
			self.alias[newKey] = self.alias[existingKey]
		elif existingKey in self.stack:
			self.alias[newKey] = existingKey
		else:
			print("Alias must correspond to a show on the stack or an previously aliased name.")

	def removeAlias(self, alias):
		del self.alias[alias]

	def addStack(self, show, ep=1):
		self.stack[show] = ep

	def addUrl(self, anime, url):
		self.url[anime] = url

	def getStack(self):
		return(self.stack)

