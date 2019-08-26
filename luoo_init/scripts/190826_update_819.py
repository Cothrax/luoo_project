from elasticsearch import Elasticsearch
client = Elasticsearch(hosts=['127.0.0.1'], timeout=20)


def update_819():
    response = client.search(
        index='luoo1',
        body={'query': {'match': {'id': 819}}}
    )
    data = response['hits']['hits'][0]
    obj_id = data['_id']
    pieces = data['_source']['pieces']
    pieces[0]['file_url'] = 'http://mp3-cdn2.luoo.net/low/luoo/radio819/01.mp3'

    client.update(
        index='luoo1',
        id=obj_id,
        body={'doc': {'pieces': pieces}}
    )


update_819()