import os
from os.path import dirname, abspath, join


def cp_covers():
    FROM_DIR = '/media/cothrax/0C05067B0C05067B/Luoo/vols'
    TO_DIR = join(dirname(dirname(abspath(__file__))), 'static/img/')
    if not os.path.exists(TO_DIR):
        os.mkdir(TO_DIR)
    for each in os.listdir(FROM_DIR):
        os.popen('cp %s %s' % (join(FROM_DIR, each, 'cover.jpg'),
                               join(TO_DIR, "%s.jpg" % str(int(each)))))
        pass


def make_black_white(file_path, opt_path):
    pass


if __name__ == '__main__':
    cp_covers()
