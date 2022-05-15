# #!usr/bin/env python3
# import string
# import re
#
# s = set()
#
# with open('ru/test_ru', 'r') as f:
#     for line in f:
#         line = re.sub(fr'[{string.punctuation + string.digits}]', '', line)
#         s = s.union(set(line))
#
#
# s = ''.join(s).lower()
# s = set(s)
# print(''.join(s))

alpha = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя".lower()
alpha = set(alpha)
print(''.join(alpha))