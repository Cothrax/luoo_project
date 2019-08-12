import logging
import time
import traceback
import os

from luoo_init.models.es_types import VolType, PieceType, VOL_INDEX
from elasticsearch.exceptions import TransportError
from luoo_init.utils.netease import NeteaseAPI
from luoo_init.utils.mysql import LuooMysqlData, DEFAULT_PIECE_VARCHAR, DEFAULT_VOL_VARCHAR

LOG_PATH = 'logs/es.log'
logger = logging.getLogger(LOG_PATH)
logger.addHandler(logging.FileHandler(LOG_PATH))
logger.setLevel(logging.WARNING)
logger.warning('[WARNING] logger started %s', time.strftime('%x %X', time.localtime()))


def insert_luoo_data(start, limit):
    data = LuooMysqlData()
    api = NeteaseAPI()
    count = 0
    for vol_data in data.vols(start, limit):
        print("parse vol %s: %s" % (vol_data['id'], vol_data['title']))
        vol = VolType()
        for each in DEFAULT_VOL_VARCHAR:
            setattr(vol, each, vol_data[each])

        # vol.suggest
        vol.pieces = []
        for piece_data in data.pieces(vol.id):
            print('\tparse piece %s %s %s' %
                  (piece_data['id'], piece_data['title'], piece_data['artist']))
            piece = PieceType()
            for each in DEFAULT_PIECE_VARCHAR:
                setattr(piece, each, piece_data[each])
            try:
                ne_id, score = api.get_id(piece.title, piece.artist, piece.album)
            except Exception as e:
                print(e)
                traceback.print_exc()
                logger.warning("[WARNING] stop at %s", start + count)
                return

            if ne_id is None:
                logger.error('[ERROR] cannot get %s->%s', vol.id, piece_data)
            elif score < 0.5:
                logger.error('[ERROR] mismatch(%s): get %s for %s->%s',
                             score, ne_id, vol.id, piece_data)
                ne_id = None
            print("get %s (sim = %s)" % (ne_id, score))
            piece.ne_id = ne_id
            piece.ne_sim = score
            piece.cover_url = [piece.cover_url, api.get_cover_url(ne_id)]

            vol.pieces.append(piece)
        try:
            vol.save(index=VOL_INDEX)
            count += 1
        except TransportError as e:
            print(e)
            traceback.print_exc()
            logger.warning("[WARNING] stop at %s", start + count)


if __name__ == "__main__":
    insert_luoo_data(394, 1)

