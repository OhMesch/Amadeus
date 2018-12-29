import sys
import os
sys.path.append(os.getcwd()+'\\src')

from CrunchyWebScraper import CrunchyWebScraper

print("Grab Goblin Links")
eps = CrunchyWebScraper.scrapeUrlForLinks("https://www.crunchyroll.com/goblin-slayer")
for ep in eps:
	print(ep)

print("\nGrab One Piece Links")
eps = CrunchyWebScraper.scrapeUrlForLinks("https://www.crunchyroll.com/one-piece")
for ep in eps:
	print(ep)