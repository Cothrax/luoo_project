from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, Completion, Keyword, Text, Integer, InnerDoc, Float
from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=['127.0.0.1'])

VOL_INDEX = 'luoo1'


class PieceType(InnerDoc):
    ne_id = Integer()
    ne_sim = Float()
    id = Integer()
    title = Text(analyzer='ik_max_word')
    album = Text(analyzer='ik_max_word')
    artist = Text()
    file_url = Keyword()
    cover_url = Keyword()


class VolType(DocType):
    suggest = Completion(analyzer='ik_max_word', search_analyzer='ik_max_word')
    id = Integer()
    title = Text(analyzer='ik_max_word')
    creat_date = Date()
    piece_num = Integer()
    pieces = Nested(PieceType, include_in_root=True)
    tag = Text(analyzer='ik_max_word')
    vol_desc = Text(analyzer='ik_max_word')

    class Meta:
        index = VOL_INDEX
        doc_type = 'vol'


if __name__ == '__main__':
    VolType.init(index=VOL_INDEX)
