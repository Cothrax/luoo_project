import MySQLdb
import MySQLdb.cursors

MYSQL_HOST = '127.0.0.1'
MYSQL_USER = 'root'
MYSQL_PASSWD = 'root'
MYSQL_DB = 'luoo'
DEFAULT_VOL_VARCHAR = ('id', 'title', 'creat_date', 'piece_num', 'tag', 'vol_desc')
DEFAULT_PIECE_VARCHAR = ('id', 'title', 'album', 'artist', 'cover_url', 'file_url')


class LuooMysqlData:
    def __init__(self):
        self.conn = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DB,
                                    charset="utf8mb4", use_unicode=True)
        self.cursor = self.conn.cursor()

    def vols(self, start, limit, varchar_list=DEFAULT_VOL_VARCHAR):
        mysql_cmd = "select %s from Vols1 where id >= %s order by id asc limit %s" \
                    % (','.join(varchar_list), start, limit)
        self.cursor.execute(mysql_cmd)
        for each in self.cursor.fetchall():
            yield {varchar_list[i]: each[i] for i in range(0, len(varchar_list))}

    def pieces(self, vol_id, varchar_list=DEFAULT_PIECE_VARCHAR):
        mysql_cmd = "select %s from Pieces1 where vol = %s order by id asc" \
                    % (','.join(varchar_list), vol_id)
        self.cursor.execute(mysql_cmd)
        for each in self.cursor.fetchall():
            yield {varchar_list[i]: each[i] for i in range(0, len(varchar_list))}

    def __del__(self):
        self.conn.close()


def debug():
    data = LuooMysqlData()
    for vol in data.vols(100, 3):
        print(vol)
        for piece in data.pieces(vol["id"]):
            print(piece)


if __name__ == '__main__':
    debug()



