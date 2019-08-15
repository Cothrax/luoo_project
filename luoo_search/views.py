import re
from django.http import Http404
from django.shortcuts import render
from elasticsearch_dsl import connections, Search, Q
from elasticsearch import Elasticsearch
from luoo_search.utils import changeChineseNumToArab, check_url
from luoo_init.utils.netease import NeteaseAPI
from random import randint
# connections.create_connection(hosts=['144.34.156.145'])
client = Elasticsearch(hosts=['127.0.0.1'], timeout=20)
api = NeteaseAPI()

TOTAL_NUM = 992
IGNORED_VOLS = [544, 566, 567, 568]


def get_search_body(keywords, keys, page_id):
    if not keywords:
        return {
            "query": {"match_all": {}},
            "sort": ["id"],
            "from": (page_id - 1) * 10,
            "size": 10,
            "_source": keys + ["creat_date"]
        }

    num_list = re.split('\D+', changeChineseNumToArab(keywords))
    id_queries = [{"match": {"id": int(i)}} for i in num_list if i]
    kw_query = {
        "multi_match": {
            "query": keywords,
            "fields": ["title^0.2", "tag^0.2", "vol_desc^0.1",
                       "pieces.title^0.1", "pieces.artist^0.1", "pieces.album^0.1"]
        }
    }
    return {
        "query": {"bool": {"should": id_queries + [kw_query]}},
        "from": (page_id - 1) * 10,
        "size": 10,
        "highlight": {
            "fields": {key: {} for key in keys},
            "pre_tags": "<strong>",
            "post_tags": "</strong>"
        },
        "_source": keys + ["creat_date"]
    }


def index(request):
    return render(request, "new_index.html")


def search(request):
    keywords = request.GET.get('q', '')
    # is_all = int(request.GET.get('all', 0))
    page_id = int(request.GET.get('p', 1))

    keys = ["id", "title", "tag", "vol_desc"]

    response = client.search(
        index="luoo1",
        body=get_search_body(keywords, keys, page_id)
    )

    total_num = response['hits']['total']['value']
    hit_list = []
    for hit in response['hits']['hits']:
        source = hit['_source']
        highlight = hit.get('highlight', {})

        hit_dict = {}
        for key in keys:
            hit_dict[key] = highlight.get(key, [source[key]])[0]
        hit_dict["creat_date"] = source.get("creat_date")
        hit_dict['cover_url'] = "img/%s.jpg" % hit_dict['id']

        if 'tag' in hit_dict:
            html_list = map(lambda x: x[1:], re.split(',', hit_dict['tag']))
            raw_list = map(lambda x: x[1:], re.split(',', source['tag']))
            hit_dict['tag'] = zip(html_list, raw_list)

        hit_list.append(hit_dict)

    return render(request, "new_result.html", {"hit_list": hit_list,
                                               "keywords": keywords,
                                               "total_num": total_num,
                                               'page_id': page_id})


def page(request, vol_id):
    response = client.search(
        index='luoo1',
        body={"query": {"match": {"id": int(vol_id)}}}
    )

    if not response['hits']['total']['value']:
        raise Http404("Vol does not exist")

    # import json
    # json.dump(response, open('response.json', 'w'))

    hit = response['hits']['hits'][0]['_source']
    hit['cover_url'] = 'img/%s.jpg' % hit['id']
    hit['vol_desc'] = re.sub('\n', '<br/>', hit['vol_desc'])

    for piece in hit.get('pieces', {}):
        # print(piece.get('ne_id'))
        piece['alter_cover_url'] = piece['cover_url'][1] if len(piece['cover_url']) > 1 else ""
        piece['cover_url'] = piece['cover_url'][0]

        # if not check_url(piece['file_url']):
        #     piece['file_url'] = api.get_file_url('file_url')
        if 'ne_id' in piece:
            piece['ne_url'] = api.get_page_url(piece['ne_id'])

    if 'tag' in hit:
        hit['tag'] = list(map(lambda x: x[1:], re.split(',', hit['tag'])))

    if hit['id'] > 1:
        hit['prev_id'] = hit['id']-1
        if hit['prev_id'] in IGNORED_VOLS:
            hit['prev_id'] -= 1

        hit['next_id'] = hit['id'] + 1
        if hit['next_id'] in IGNORED_VOLS:
            hit['next_id'] += 1
    return render(request, 'new_page.html', hit)


def search_song(request):
    keywords = request.GET.get('q', '')
    match_query = {
        "multi_match": {
            "query": keywords,
            "fields": ["pieces.title", "pieces.artist", "pieces.album"]
        }
    }
    response = client.search(
        index='luoo1',
        body={
            'query': {
                'nested': {
                    "path": "pieces",
                    "query": match_query,
                    "score_mode": "avg",
                    "inner_hits": {"size": 50}
                }
            },
            "_source": ["id"]
        }
    )
    hit_list = []
    count = 0
    for hit in response['hits']['hits']:
        for each in hit['inner_hits']['pieces']['hits']['hits']:
            hit_dict = each['_source']
            hit_dict['vol_id'] = hit['_source']['id']

            hit_dict['alter_cover_url'] = hit_dict['cover_url'][1]
            hit_dict['cover_url'] = hit_dict['cover_url'][0]
            count += 1
            hit_dict['id'] = count

            if 'ne_id' in hit_dict:
                hit_dict['ne_url'] = api.get_page_url(hit_dict['ne_id'])

            hit_list.append(hit_dict)

    # print(hit_list)
    return render(request, 'new_search_song.html', {'hit_list': hit_list,
                                                    'total_num': count,
                                                    'keywords': keywords})


if __name__ == '__main__':
    search(None)
