import sys
import os
from random import randint
import pytest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from amadeus.CrunchyWebScraper import CrunchyWebScraper


@pytest.fixture(scope="function")
def unique_crunchy_web_scraper():
    return CrunchyWebScraper(3, 5, 60)

@pytest.fixture(scope="function")
def unique_now_seconds():
    return int(time.time())

class TestCrunchyScraper():
    def test_clean_request_1(self, unique_crunchy_web_scraper): 
        unique_crunchy_web_scraper.cleanRequests()
        assert len(unique_crunchy_web_scraper.requests_log.keys()) == 0

    @pytest.mark.parametrize("value", [
        65,
        61
    ])
    def test_clean_request_2(self, unique_crunchy_web_scraper, unique_now_seconds, value): 
        unique_crunchy_web_scraper.requests_log[unique_now_seconds - value] = 5
        unique_crunchy_web_scraper.cleanRequests(unique_now_seconds)
        assert len(unique_crunchy_web_scraper.requests_log.keys()) == 0

    @pytest.mark.parametrize("value", [
        60,
        0
    ])
    def test_clean_request_3(self, unique_crunchy_web_scraper, unique_now_seconds, value): 
        unique_crunchy_web_scraper.requests_log[unique_now_seconds] = 5
        unique_crunchy_web_scraper.cleanRequests(unique_now_seconds)
        assert len(unique_crunchy_web_scraper.requests_log.keys()) == 1

    def test_log_request(self, unique_crunchy_web_scraper): 
        unique_crunchy_web_scraper.logRequest(2)
        first_key = list(unique_crunchy_web_scraper.requests_log.keys())[0]
        assert unique_crunchy_web_scraper.requests_log[first_key] == 2
    
    def test_get_total_requests_1(self, unique_crunchy_web_scraper): 
        assert unique_crunchy_web_scraper.getTotalRequests() == 0

    @pytest.mark.parametrize("value", [
        1,
        2,
        100
    ])
    def test_get_total_requests_2(self, unique_crunchy_web_scraper, value):
        unique_crunchy_web_scraper.logRequest(value)
        assert unique_crunchy_web_scraper.getTotalRequests() == value

    def test_throttle_requests_1(self, unique_crunchy_web_scraper, unique_now_seconds): 
        unique_crunchy_web_scraper.requests_log[unique_now_seconds - 5] = 1
        unique_crunchy_web_scraper.requests_log[unique_now_seconds] = 1
        unique_crunchy_web_scraper.throttleRequests(1)

    def test_throttle_requests_2(self, unique_crunchy_web_scraper, unique_now_seconds): 
        unique_crunchy_web_scraper.requests_log[unique_now_seconds - 5] = 1
        unique_crunchy_web_scraper.requests_log[unique_now_seconds] = 1
        with pytest.raises(Exception):
            unique_crunchy_web_scraper.throttleRequests(2)

    def test_throttle_requests_3(self, unique_crunchy_web_scraper, unique_now_seconds): 
        unique_crunchy_web_scraper.requests_log[unique_now_seconds - 6] = 1
        unique_crunchy_web_scraper.requests_log[unique_now_seconds] = 1
        unique_crunchy_web_scraper.throttleRequests(2)

    def test_throttle_requests_4(self, unique_crunchy_web_scraper, unique_now_seconds): 
        unique_crunchy_web_scraper.requests_log[unique_now_seconds - 5] = 2
        unique_crunchy_web_scraper.requests_log[unique_now_seconds] = 1
        with pytest.raises(Exception):
            unique_crunchy_web_scraper.throttleRequests(1)

    def test_throttle_requests_5(self, unique_crunchy_web_scraper, unique_now_seconds): 
        with pytest.raises(Exception):
            unique_crunchy_web_scraper.throttleRequests(4)

    # NEED TESTS FOR getHTMLFromURL
    # NEED TESTS FOR getEpisodeLinksFromHTML

    # NEED TESTS FOR scrapeUrlForEpisodeLinks
    # def test_scrapeUrlForEpisodeLinks(self, unique_crunchy_web_scraper): 
    #     eps = unique_crunchy_web_scraper.scrapeUrlForEpisodeLinks("https://www.crunchyroll.com/one-piece")
    #     insert assert here

    # NEED TESTS FOR getEpisodeLink
    # @pytest.mark.parametrize("value", [
    #     "6",
    #     6
    # ])
    # def test_getEpisodeLink(self, unique_crunchy_web_scraper, value): 
    #     eps = unique_crunchy_web_scraper.getEpisodeLink("https://www.crunchyroll.com/goblin-slayer", value)
    #     insert assert here

# Refactor this test
# print("\nGrab 5 random one-piece eps")
# for i in range(5):
#     reqEp = randint(0,1000)
#     print("Grabbing episode {0}".format(reqEp))
#     ep = CrunchyWebScraper.getEpisodeLink("https://www.crunchyroll.com/one-piece", str(reqEp))
#     if ep:
#         print("\t"+ep)
#     else:
#         print("\tNo episode {0}".format(reqEp))

# Refactor this test (or maybe not? not too many requests in the unittests...)
# print("\nGet JoJo Ep 1 from each Season")
# eps = CrunchyWebScraper.scrapeUrlForEpisodeLinks("https://www.crunchyroll.com/jojos-bizarre-adventure")
# for i in range(1, 6):
#     print("Season {0}:".format(i))
#     epLink = CrunchyWebScraper.getEpisodeLink("https://www.crunchyroll.com/jojos-bizarre-adventure", "1", str(i))
#     print(epLink)