import requests
import re
import time
from bs4 import BeautifulSoup
from collections import defaultdict

# probably should abstract the throttle stuff
class CrunchyWebScraper():
    def __init__(self, throttle_max = 10, throttle_period_seconds = 10, 
            time_save_req_seconds = 60 * 60):
        self.requests_log = defaultdict(int)
        self.throttle_max = throttle_max
        self.throttle_period_seconds = throttle_period_seconds
        self.time_save_req_seconds = time_save_req_seconds

    @property
    def now_seconds(self):
        return int(time.time())
    
    # keeps data inclusivley from self.now_seconds - self.time_save_req_seconds
    # could change algorithm here, or clean at less frequent intervals. with a larger
    # time_save_req_seconds this could be slow. OrderedDict would also work
    def cleanRequests(self, now_seconds = None):
        if not now_seconds:
            now_seconds = self.now_seconds
        for date in list(self.requests_log.keys()):
            print(date)
            print(now_seconds - self.time_save_req_seconds)
            if date < now_seconds - self.time_save_req_seconds:
                del self.requests_log[date]

    # 0 returns current second
    def getTotalRequests(self, seconds_back = None):
        total = 0
        for date in self.requests_log:
            if not seconds_back or date < self.now_seconds - seconds_back:
                total += self.requests_log[date]
        return total

    def throttleRequests(self, num_requests):
        total = 0
        start = self.now_seconds - self.throttle_period_seconds
        for date in range(start, start + self.throttle_period_seconds + 1):
            total += self.requests_log[date]
        if total + num_requests > self.throttle_max:
            raise Exception("Throttle violation (429) in CrunchyWebScraper." + 
                " You tried to make {0} requests when you have already used".format(num_requests) + 
                " {0} requests in the last {1} seconds".format(total, self.throttle_period_seconds))
        self.logRequest(num_requests)

    def logRequest(self, num_requests):
        self.cleanRequests()
        self.requests_log[self.now_seconds] += num_requests

    def getEpisodeLink(url, requested_ep, season = "1"):
        eps_across_seasons = []
        all_eplinks = self.scrapeUrlForEpisodeLinks(url)
        for ep_link in all_eplinks:
            episodeNum = ep_link.split('/')[4].split('-')[1]
            if episodeNum == str(requested_ep):
                eps_across_seasons.append(ep_link)
        if eps_across_seasons:
            return eps_across_seasons[::-1][int(season)-1]
    
    def scrapeUrlForEpisodeLinks(url):
        try:
            html_soup = self.getHTMLFromURL(url)
        except requests.exceptions.RequestException as err:
            print("Unable to reach {}:\n{}\n".format(url, err))
        else:
            titleString = url.split("/")[-1]
            return self.getEpisodeLinksFromHTML(html_soup, titleString)

    def getHTMLFromURL(url):
        self.throttleRequests(1)
        code = requests.get(url)
        html_plain_text = code.text
        html_soup = BeautifulSoup(html_plain_text, "html.parser")
        return html_soup

    def getEpisodeLinksFromHTML(html, title):
        base_url = "https://www.crunchyroll.com"
        episode_links = []
        for link in html.find_all(href=re.compile(title + "/episode")): 
            new_url = link.get('href')
            episode_links.append(base_url + new_url)
        return episode_links