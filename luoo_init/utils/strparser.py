import sys
sys.setrecursionlimit(5000)


FILTER_WORDS = ['sex', 'fuck', 'dick']


def cached(func):
    cache = {}

    def wrapper(*args):
        res = cache.get(args)
        if res is None:
            res = cache[args] = func(*args)
        return res
    return wrapper


def filter_str(s):
    for each in FILTER_WORDS:
        idx = s.find(each)
        if idx != -1:
            s = s[:idx] + ' ' + s[idx + 1:]
    return s


def similarity(s: str, t: str) -> float:
    s = s.lower().replace(' ', '')
    t = t.lower().replace(' ', '')

    @cached
    def lcs(i, j):
        if i == 0 or j == 0:
            return 0
        return max(lcs(i - 1, j), lcs(i, j - 1),
                   lcs(i - 1, j - 1) + 1 if s[i - 1] == t[j - 1] else 0)

    l = lcs(len(s), len(t))
    return (l / len(s) + l / len(t)) / 2 if l else 0


if __name__ == '__main__':
    x = 'zapavietyaposzniahastarca'
    y = 'крыжы-абярэгi'
    print(similarity(x, y))

