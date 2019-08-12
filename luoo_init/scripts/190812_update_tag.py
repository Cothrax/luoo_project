from elasticsearch import Elasticsearch
client = Elasticsearch(hosts=['127.0.0.1'], timeout=20)


def update_tag():
    """清除[EMPTY]的tag"""
    client.update_by_query