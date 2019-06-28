import sys
import os
sys.path.append(os.getcwd()+'\\src')

from Amadeus import Amadeus
from CrunchyWebScraper import CrunchyWebScraper

print("Amadeas Testing")
driver = Amadeus()
print("\nInitalized as:")
print(driver)

print("Add alias Garbage:")
driver.addAlias("123","456")
print("Add SlimeLongName to stack")
driver.addStack("SlimeLongName")
print("Add alias Slime to SlimeLongName")
driver.addAlias("SlimeLongName", "Slime")
print("Add alias BigSlime to Slime")
driver.addAlias("Slime", "BigSlime")
print(driver)

print("\nDelete BigSlime.")
driver.removeAlias("BigSlime")
print("Delete more Garbage.")
driver.removeAlias("CASDF")
print(driver)

inStr = "DearPhilip"
print("\nAdd Stack {0}".format(inStr))
driver.addStack(inStr)
print(driver.getStack())
print("Remove stack {0}".format(inStr))
driver.removeStack(inStr)
print(driver.getStack())
print("Remove stack {0} again".format(inStr))
driver.removeStack(inStr)
print(driver.getStack())

print("Add JoJo's on season 3")
jojoUrl = "https://www.crunchyroll.com/jojos-bizarre-adventure"
def cleanAnimeName(dirtyName):
    animeNameLower = dirtyName.replace('-',' ').lower()
    animeNameClean = " ".join(list(map(lambda x: x.capitalize(), animeNameLower.split())))
    return(animeNameClean)
animeNameClean = cleanAnimeName(jojoUrl.split("/")[-1])
driver.addUrl(animeNameClean, jojoUrl)
driver.addStack(animeNameClean)
driver.setSeason(animeNameClean, "2")
driver.addAlias(animeNameClean, "jojo")
print(driver)

print("Get Episode 1")
trueTitle = driver.getTitleFromKey("jojo")
print(CrunchyWebScraper.getEpisodeLink(driver.url[trueTitle], "1", driver.season[trueTitle]))