# -*- coding: UTF-8 -*-

import math
# raw_type_dict = {
#     "耕地": ["水田", "旱地"],
#     "园地": ["果园", "茶园"]
# }
# type_dict = {}
#
#
# def create_type_dict(raw_dict):
#     return {child: prt for prt in raw_dict.keys() for child in raw_dict[prt]}
#
# type_dict = create_type_dict(raw_type_dict)
#
# for k, v in type_dict.items():
#     print k, v
#
# director_span = 2 * math.pi / 16.0
#
#
# def test(a):
#     angle = a + 0.5 * director_span
#     if angle >= 2 * math.pi:
#         angle -= 2 * math.pi
#     print str(int(angle / director_span) + 1)
#
#
# test(-1)


def a(b, *c):
    print b
    if c:
        print "a"

a(5, 5)
a(5)