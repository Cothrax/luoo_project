from elasticsearch import Elasticsearch
client = Elasticsearch(hosts=['127.0.0.1'], timeout=20)


def update_tag():
    """清除[EMPTY]的tag"""
    client.update_by_query(
        index='luoo1',
        body={
            "script": {
                "source": "ctx._source.tag=''",
                "lang": "painless"
            },
            "query": {
                "match": {
                    "tag": "empty"
                }
            }
        }
    )


if __name__ == '__main__':
    update_tag()