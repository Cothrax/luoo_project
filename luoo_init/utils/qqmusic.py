from urllib import request
import requests
import json
import time
from random import randint
from urllib.parse import urljoin, quote
from luoo_init.utils.strparser import  filter_str, similarity as sim

DEFAULT_API_URL = 'http://localhost:3200'
PAGE_URL = 'https://y.qq.com/n/yqq/song/%s.html'

def valid_url(song_url):
    if not song_url:
        return False
    try:
        with request.urlopen(song_url) as song:
            if song.status < 200 or song.status >= 300:
                return False
    except Exception as e:
        return False
    return True

class QQMusicAPI:
    def __init__(self, api_url=DEFAULT_API_URL):
        self.api_url = api_url

    def query(self, url, params):
        r = requests.get(urljoin(self.api_url, url), params=params)
        res = json.loads(r.text)
        time.sleep(randint(3, 5) / 10.0)
        # if 200 <= int(res['code']) < 300:
        if res['response']['code'] == 0:
            return res
        else:
            raise ConnectionError('cannot get %d (return %s)', r.url, r.text)

    def key_search(self, key_str):
        # print(key_str)
        search_url = '/getSearchByKey'
        params = {'key': key_str}
        return self.query(search_url, params)

    def get_id(self, title, artist, album, if_check=False, depth=5):
        keywords = "%s %s" % (title, album)
        res = self.key_search(filter_str(keywords.lower()))
        hit_list = [e['mid'] for e in res['response']['data']['song']['list']]

        best_score = 0
        best_id = None
        count = 0
        for song_id in hit_list:
            if count > depth:
                break

            details = self.query('/getSongInfo', {'songmid': song_id})
            details = details['response']['songinfo']['data']['track_info']
            s_title = details['name']
            s_album = details['album']['name']
            try:
                s_artist = details['singer'][0]['name']
            except Exception as e:
                print(e)
                s_artist = ''

            score = sim(s_title, title) * 0.5 + sim(s_artist, artist) * 0.4 + sim(s_album, album) * 0.1

            # print(s_title, s_album, s_artist, score)

            if score > best_score:
                if if_check and not valid_url(self.get_file_url(song_id)):
                    continue

                best_id = song_id
                best_score = score
                # cover_url = detail['songs'][0]['al']['picUrl']

            count += 1
            if best_score > 0.9:
                break
        return best_id, best_score

    def get_file_url(self, song_id):
        if not song_id:
            return None
        try:
            res = self.query('/getMusicVKey', {'songmid': song_id})
            return res['response']['playLists'][0]
        except Exception as e:
            print('error getting qqmusic url of %s' % song_id)
            print(e)
            return None

    def get_cover_url(self, song_id):
        pass

    @staticmethod
    def get_page_url(song_id):
        return PAGE_URL % song_id


def debug():
    api = QQMusicAPI()
    # song_id, score = api.get_id('Maybe i maybe you', 'scorpions', 'unbreakable')
    # print(song_id, score)
    # print(api.get_file_url(song_id))
    print(api.get_file_url('003SO4OV0KkgVs'))


if __name__ == '__main__':
    debug()