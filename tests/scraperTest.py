import sys
import os
from random import randint

sys.path.append(os.getcwd()+'\\src')

from CrunchyWebScraper import CrunchyWebScraper

print("Grab Goblin Links")
eps = CrunchyWebScraper.scrapeUrlForEpisodeLinks("https://www.crunchyroll.com/goblin-slayer")
for ep in eps:
    print(ep)

print("\nGrab One Piece Links")
eps = CrunchyWebScraper.scrapeUrlForEpisodeLinks("https://www.crunchyroll.com/one-piece")
for ep in eps:
    print(ep)

print("\nGrab Goblin Ep 6")
ep = CrunchyWebScraper.getEpisodeLink("https://www.crunchyroll.com/goblin-slayer", "6")
print(ep)

print("\nGrab 5 random one-piece eps")
for i in range(5):
    reqEp = randint(0,1000)
    print("Grabbing episode {0}".format(reqEp))
    ep = CrunchyWebScraper.getEpisodeLink("https://www.crunchyroll.com/one-piece", str(reqEp))
    if ep:
        print("\t"+ep)
    else:
        print("\tNo episode {0}".format(reqEp))

print("\nJoJo's Links")
eps = CrunchyWebScraper.scrapeUrlForEpisodeLinks("https://www.crunchyroll.com/jojos-bizarre-adventure")
for ep in eps:
    print(ep)

print("\nGet JoJo Ep 1 from each Season")
eps = CrunchyWebScraper.scrapeUrlForEpisodeLinks("https://www.crunchyroll.com/jojos-bizarre-adventure")
for i in range(1,6):
    print("Season {0}:".format(i))
    epLink = CrunchyWebScraper.getEpisodeLink("https://www.crunchyroll.com/jojos-bizarre-adventure", "1", str(i))
    print(epLink)