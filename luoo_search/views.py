import re
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from elasticsearch_dsl import connections, Search, Q
from elasticsearch import Elasticsearch
from luoo_search.utils import changeChineseNumToArab, check_url
from luoo_init.utils.netease import NeteaseAPI
from luoo_init.utils.qqmusic import QQMusicAPI, valid_url
from .models import QQ, Netease
from random import randint
# connections.create_connection(hosts=['144.34.156.145'])
client = Elasticsearch(hosts=['127.0.0.1'], timeout=20)
ne_api = NeteaseAPI(api_url='http://118.24.119.64:3000/')
qq_api = QQMusicAPI(api_url='http://118.24.119.64:3200/')

TOTAL_NUM = 992
IGNORED_VOLS = [544, 566, 567, 568]
NULL_FILE = '/static/null.m4v'


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

        parse_file_url(piece)
        # print(piece['file_url'])
        # if not check_url(piece['file_url']):
        #     piece['file_url'] = api.get_file_url('file_url')
        # if 'ne_id' in piece:
        #     piece['ne_url'] = ne_api.get_page_url(piece['ne_id'])

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

            # customized url
            parse_file_url(hit_dict)

            # if 'ne_id' in hit_dict:
            #     hit_dict['ne_url'] = api.get_page_url(hit_dict['ne_id'])

            hit_list.append(hit_dict)

    # print(hit_list)
    return render(request, 'new_search_song.html', {'hit_list': hit_list,
                                                    'total_num': count,
                                                    'keywords': keywords})


def parse_file_url(piece):
    file_url = '/luoo/file/?ne=%s&qq=%s'
    ne_str = ''
    qq_str = ''
    if 'ne_id' in piece and piece['ne_sim'] > 0.75:
        ne_str = str(piece['ne_id'])
        piece['ne_url'] = ne_api.get_page_url(piece['ne_id'])
    if 'qq_id' in piece and piece['qq_sim'] > 0.75:
        qq_str = str(piece['qq_id'])
        piece['qq_url'] = qq_api.get_page_url(piece['qq_id'])

    if not ne_str and not qq_str:
        if min(piece['ne_sim'], piece['qq_sim']) > 0.60:
            if piece['qq_sin'] >= piece['ne_sim']:
                qq_str = str(piece['qq_id'])
                piece['qq_url'] = qq_api.get_page_url(piece['qq_id'])
            else:
                ne_str = str(piece['ne_id'])
                piece['ne_url'] = ne_api.get_page_url(piece['ne_id'])

    piece['file_url'] = file_url % (ne_str, qq_str)
    if ne_str or qq_str:
        piece['href'] = 'qq' if piece['qq_sim'] >= piece['ne_sim'] else 'ne'


def file(request):
    qq_id = str(request.GET.get('qq', ''))
    ne_id = str(request.GET.get('ne', ''))
    print(ne_id, qq_id)
    file_url = None
    if qq_id:
        songs = QQ.objects.filter(song_id=qq_id)
        if not len(songs):
            file_url = qq_api.get_file_url(qq_id)
            qq_song = QQ(song_id=qq_id, song_url=file_url or '')
            qq_song.save()
        else:
            qq_song = songs[0]
            if not valid_url(qq_song.song_url):
                qq_song.song_url = qq_api.get_file_url(qq_id) or ''
                qq_song.save()
            else:
                return redirect(qq_song.song_url)
            file_url = qq_song.song_url

    if (not file_url or not valid_url(file_url)) and ne_id:

        songs = Netease.objects.filter(song_id=ne_id)
        if not len(songs):
            file_url = ne_api.get_file_url(ne_id)
            ne_song = Netease(song_id=ne_id, song_url=file_url)
            ne_song.save()
        else:
            ne_song = songs[0]
            if not valid_url(ne_song.song_url):
                ne_song.song_url = ne_api.get_file_url(ne_id)
                ne_song.save()
            else:
                return redirect(ne_song.song_url)
            file_url = ne_song.song_url

    return redirect(file_url or NULL_FILE)


if __name__ == '__main__':
    search(None)
