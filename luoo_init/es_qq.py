from luoo_init.utils.qqmusic import QQMusicAPI
from elasticsearch import Elasticsearch

client = Elasticsearch(hosts=['144.34.156.145'], timeout=20)


def insert_qq(gte, lte, max_tries=5):
    api = QQMusicAPI()
    query_body = {
        'range': {
            'id': {
                'gte': gte,
                'lte': lte
            }
        }
    }

    response = client.search(index='luoo1', body={'size': lte - gte + 1, "sort": ["id"], 'query': query_body})
    print('total: ', len(response['hits']['hits']))
    for vol in response['hits']['hits']:
        obj_id = vol['_id']
        print('vol. ', vol['_source']['id'])
        if 'pieces' not in vol['_source']:
            continue
        pieces = vol['_source']['pieces']
        for i in range(len(pieces)):
            title = pieces[i]['title']
            album = pieces[i]['album']
            artist = pieces[i]['artist']
            qq_id, qq_sim = api.get_id(title, artist, album, if_check=True)
            pieces[i]['qq_id'] = qq_id
            pieces[i]['qq_sim'] = qq_sim
            print('%s %s %s: %s %s' % (title, album, artist, api.get_page_url(qq_id), qq_sim))

        tries = 0
        while True:
            try:
                client.update(
                    index='luoo1',
                    id=obj_id,
                    body={'doc': {'pieces': pieces}}
                )
                break
            except Exception as e:
                tries += 1
                if tries == max_tries:
                    raise e


def insert_qq_again(gte, lte, max_tries=5):
    api = QQMusicAPI()
    query_body = {
        'range': {
            'id': {
                'gte': gte,
                'lte': lte
            }
        }
    }

    response = client.search(index='luoo1', body={'size': lte - gte + 1, "sort": ["id"], 'query': query_body})
    print('total: ', len(response['hits']['hits']))
    for vol in response['hits']['hits']:
        obj_id = vol['_id']
        print('vol. ', vol['_source']['id'])
        if 'pieces' not in vol['_source']:
            continue
        pieces = vol['_source']['pieces']
        count = 0
        for i in range(len(pieces)):

            if pieces[i].get('qq_sim', 0) >= 0.75:
                continue
            if pieces[i].get('ne_sim', 0) >= 0.75:
                continue

            title = pieces[i]['title']
            album = pieces[i]['album']
            artist = pieces[i]['artist']
            qq_id, qq_sim = api.get_id(title, artist, album, if_check=True)
            if qq_sim > pieces[i].get('qq_sim', 0):
                pieces[i]['qq_id'] = qq_id
                pieces[i]['qq_sim'] = qq_sim
                print('%s %s %s: %s %s' % (title, album, artist, api.get_page_url(qq_id), qq_sim))
                count += 1

        if not count:
            continue

        tries = 0
        while True:
            try:
                client.update(
                    index='luoo1',
                    id=obj_id,
                    body={'doc': {'pieces': pieces}}
                )
                break
            except Exception as e:
                tries += 1
                if tries == max_tries:
                    raise e


def miss_stat(gte, lte):
    api = QQMusicAPI()
    query_body = {
        'range': {
            'id': {
                'gte': gte,
                'lte': lte
            }
        }
    }

    response = client.search(index='luoo1', body={'size': lte - gte + 1, "sort": ["id"], 'query': query_body})
    # print('total: ', len(response['hits']['hits']))
    for vol in response['hits']['hits']:
        obj_id = vol['_id']
        print('vol. ', vol['_source']['id'])
        if 'pieces' not in vol['_source']:
            continue
        pieces = vol['_source']['pieces']
        # count = 0
        for i in range(len(pieces)):

            if pieces[i].get('qq_sim', 0) < 0.70 and pieces[i].get('ne_sim', 0) <= 0.70:
                title = pieces[i]['title']
                album = pieces[i]['album']
                artist = pieces[i]['artist']
                print('%s: %s, %s, %s, %s: %s, %s: %s' % (pieces[i]['id'], title, album, artist,
                                                  pieces[i].get('qq_id', None), pieces[i].get('qq_sim', 0),
                                                  pieces[i].get('ne_id', None), pieces[i].get('ne_sim', 0)))
                global count
                count += 1


count = 0
if __name__ == '__main__':
    # insert_qq(901, 1000)
    # bp = [0, 100, 200, 300, 400, 500, 600, 700, 750]
    # for l, r in zip(bp, bp[1:]):
    #     insert_qq_again(l+1, r)
    # insert_qq_again(751, 800)

    bp = list(range(0, 1100, 100))
    for l, r in zip(bp, bp[1:]):
        miss_stat(l, r)
    print('total: ', count)




