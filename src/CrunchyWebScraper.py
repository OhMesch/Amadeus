import requests
import re
from bs4 import BeautifulSoup

class CrunchyWebScraper(object):
	def getEpisodeLink(url, requestedEp):
		allEpLinks = CrunchyWebScraper.scrapeUrlForEpisodeLinks(url)
		for epLink in allEpLinks:
			episodeNum = epLink.split('/')[2].split('-')[1]
			if int(episodeNum) == requestedEp:
				return(epLink)

	def scrapeUrlForEpisodeLinks(url):
		try:
			htmlSoup = CrunchyWebScraper.getHTMLFromURL(url)
		except requests.exceptions.RequestException as err:
			print("Unable to reach {}:\n{}\n".format(url,err))
		else:
			titleString = url.split("/")[-1]
			return(CrunchyWebScraper.getEpisodeLinksFromHTML(htmlSoup, titleString))

	def getHTMLFromURL(url):
		code = requests.get(url)
		htmlInPlainText = code.text
		htmlSoup = BeautifulSoup(htmlInPlainText, "html.parser")
		return(htmlSoup)

	def getEpisodeLinksFromHTML(html,title):
		baseURL = "www.crunchyroll.com"
		episodeLinks = []
		for link in html.find_all(href=re.compile(title+"/episode")): 
			newUrl = link.get('href')
			episodeLinks.append(baseURL+newUrl)
		return(episodeLinks)