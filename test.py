# -*- coding: UTF-8 -*-

import math
import arcgisHelper as ah
# import arcpy

# arcpy.env.workspace = "C:/MData/TestGDB.gdb"
# arcpy.DeleteFeatures_management("C:/MData/TestGDB.gdb/BOUND_17_H2W_DS")
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


# def a(b, *c):
#     print b
#     if c:
#         print "a"
#
# a(5, 5)
# a(5)
ah.set_env("E:/InformationCenter/WorkAndHome.gdb", True)
ah.field_append(["QBM_A_"+str(n) for n in xrange(420102, 420108)] + ["QBM_A_"+str(n) for n in xrange(420111, 420122)],
                "QBM_A_Merge", "POLYGON")

ah.field_append(["QBM_L_"+str(n) for n in xrange(420102, 420108)] + ["QBM_L_"+str(n) for n in xrange(420111, 420122)],
                "QBM_L_Merge", "POLYLINE")
# print ah.field_jenks2("QBM_L_420102", "Direction", 3)
