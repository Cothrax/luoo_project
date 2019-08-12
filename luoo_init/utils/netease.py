import requests
import json
from urllib.parse import urljoin, quote
import time
from random import randint
from luoo_init.utils.strparser import filter_str, similarity as sim
from selenium import webdriver
import selenium.webdriver.support.ui as ui

DEFAULT_API_URL = 'http://localhost:3000'
DEFAULT_DRIVER_PATH = '/home/cothrax/python_proj/geckodriver-v0.24.0-linux64/geckodriver'
SEARCH_URL = 'https://music.163.com/#/search/m/?s='
PAGE_URL = 'https://music.163.com/#/song?id='
CHECK_ELEMENT_CLASS = 's-fc6'


class NeteaseAPI:
    def __init__(self, api_url=DEFAULT_API_URL, driver_path=DEFAULT_DRIVER_PATH):
        self.api_url = api_url
        self.driver_path = driver_path
        self.browser = None
        # self.proxy = 'http://5.196.255.171:3128'

    def query(self, url, params):
        # params['proxy'] = self.proxy
        r = requests.get(urljoin(self.api_url, url), params=params)

        res = json.loads(r.text)
        time.sleep(randint(3, 5) / 10.0)
        if 200 <= int(res['code']) < 300:
            return res
        else:
            raise ConnectionError('cannot get %d (return %s)', r.url, r.text)

    def selenium_search(self, keywords):
        if self.browser is None:
            self.browser = webdriver.Firefox(executable_path=self.driver_path)

        wait = ui.WebDriverWait(self.browser, 20)

        self.browser.get(SEARCH_URL + keywords)
        frame = self.browser.find_element_by_id('g_iframe')
        self.browser.switch_to_frame(frame)
        wait.until(lambda driver: driver.find_element_by_class_name(CHECK_ELEMENT_CLASS))
        wait.until(lambda driver: driver.page_source.find('加载中') == -1)

        text = self.browser.page_source
        pattern = 'song?id='
        start = text.find(pattern)

        while start != -1:
            start += len(pattern)
            end = text.find('"', start)
            yield int(text[start:end])
            start = text.find(pattern, end)

    def get_id(self, title, artist, album):
        keywords = "%s %s" % (title, artist)
        best_score = 0
        best_id = None
        count = 0
        for song_id in self.selenium_search(quote(filter_str(keywords.lower()))):
            count += 1
            if count > 5:
                break

            detail = self.query('/song/detail', {'ids': song_id})
            s_title = detail['songs'][0]['name']
            s_album = detail['songs'][0]['al']['name']
            s_artist = ' '.join((ar['name'] for ar in detail['songs'][0]['ar']))
            score = sim(s_title, title) * 0.5 + sim(s_artist, artist) * 0.4 + sim(s_album, album) * 0.1
            # print(s_title, s_album, s_artist, score)

            if score > best_score:
                best_id = song_id
                best_score = score
                # cover_url = detail['songs'][0]['al']['picUrl']
            if best_score > 0.9:
                break
        return best_id, best_score

    def get_file_url(self, song_id):
        if not song_id:
            return None
        try:
            d = self.query('/song/url', {'id': song_id})
            return d['data'][0]['url']
        except:
            return None

    def get_cover_url(self, song_id):
        if song_id is None:
            return None
        d = self.query('/song/detail', {'ids': song_id})
        try:
            return d['songs'][0]['al']['picUrl']
        except:
            return None

    @staticmethod
    def get_page_url(song_id):
        return PAGE_URL + str(song_id) if song_id else None

    def __del__(self):
        if self.browser is not None:
            self.browser.quit()


def debug():
    ne_api = NeteaseAPI()
    # song_id, score = ne_api.get_id("still love you", "scorpion", "still love you")
    # print(song_id, score)
    song_id = 28066470
    print(ne_api.get_page_url(song_id))
    print(ne_api.get_cover_url(song_id))
    print(ne_api.get_file_url(song_id))


if __name__ == '__main__':
    debug()
