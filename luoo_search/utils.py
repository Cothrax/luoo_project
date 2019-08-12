# -*- coding: cp936 -*-
from urllib.request import urlopen

common_used_numerals_tmp = {'��': 0, 'һ': 1, '��': 2, '��': 2, '��': 3, '��': 4, '��': 5, '��': 6, '��': 7, '��': 8, '��': 9,
                            'ʮ': 10, '��': 100, 'ǧ': 1000, '��': 10000, '��': 100000000}
common_used_numerals = {}
for key in common_used_numerals_tmp:
    common_used_numerals[key] = common_used_numerals_tmp[key]


def chinese2digits(uchars_chinese):
    total = 0
    r = 1  # ��ʾ��λ����ʮ��ǧ...
    for i in range(len(uchars_chinese) - 1, -1, -1):
        val = common_used_numerals.get(uchars_chinese[i])
        if val >= 10 and i == 0:  # Ӧ�� ʮ�� ʮ�� ʮ*֮��
            if val > r:
                r = val
                total = total + val
            else:
                r = r * val
                # total =total + r * x
        elif val >= 10:
            if val > r:
                r = val
            else:
                r = r * val
        else:
            total = total + r * val
    return total


num_str_start_symbol = ['һ', '��', '��', '��', '��', '��', '��', '��', '��', '��', 'ʮ']
more_num_str_symbol = ['��', 'һ', '��', '��', '��', '��', '��', '��', '��', '��', '��', 'ʮ', '��', 'ǧ', '��', '��']


def changeChineseNumToArab(oriStr):
    lenStr = len(oriStr);
    aProStr = ''
    if lenStr == 0:
        return aProStr;

    hasNumStart = False;
    numberStr = ''
    for idx in range(lenStr):
        if oriStr[idx] in num_str_start_symbol:
            if not hasNumStart:
                hasNumStart = True;

            numberStr += oriStr[idx]
        else:
            if hasNumStart:
                if oriStr[idx] in more_num_str_symbol:
                    numberStr += oriStr[idx]
                    continue
                else:
                    numResult = str(chinese2digits(numberStr))
                    numberStr = ''
                    hasNumStart = False;
                    aProStr += numResult

            aProStr += oriStr[idx]
            pass

    if len(numberStr) > 0:
        resultNum = chinese2digits(numberStr)
        aProStr += str(resultNum)

    return aProStr


def check_url(url):
    with urlopen(url) as f:
        return 200 <= f.status < 300


def debug():
    testStr = ['������ʮ��', '����������ʮ����Ǯ', 'ʮ�����ײ�', 'һ������������ٶ�ʮ��', '���������治��',
               '�ٷ�֮��ʮ discount rate�ܸ���', 'ǧ��Ҫ',
               '���invoice valueֵһ����',
               '�ҵ�һ�ټ���Ʒhave quality',
               '��һ���ҵ��ղؼ����û��һ���۾�', ]

    for tstr in testStr:
        print(tstr + ' = ' + changeChineseNumToArab(tstr))


if __name__ == '__main__':
    debug()