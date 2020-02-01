from luoo_init.utils.qqmusic import QQMusicAPI
from elasticsearch import Elasticsearch
client = Elasticsearch(hosts=['144.34.156.145'], timeout=20)


def insert_qq(gte, lte):
    api = QQMusicAPI()
    query_body = {
        'range': {
            'id': {
                'gte': gte,
                'lte': lte
            }
        }
    }

    response = client.search(index='luoo1', body={'size': lte-gte+1, 'query': query_body})
    print('total: ', len(response['hits']['hits']))
    for vol in response['hits']['hits']:
        obj_id = vol['_id']
        print('vol. ', vol['_source']['id'])
        pieces = vol['_source']['pieces']
        for i in range(len(pieces)):
            title = pieces[i]['title']
            album = pieces[i]['album']
            artist = pieces[i]['artist']
            qq_id, qq_sim = api.get_id(title, artist, album, if_check=True)
            pieces[i]['qq_id'] = qq_id
            pieces[i]['qq_sim'] = qq_sim
            print('%s %s %s: %s %s' % (title, album, artist, api.get_page_url(qq_id), qq_sim))

        client.update(
            index='luoo1',
            id=obj_id,
            body={'doc': {'pieces': pieces}}
        )


if __name__ == '__main__':
    insert_qq(25, 100)
