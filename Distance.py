# -*- coding: UTF-8 -*-
import time
import math
import arcgisHelper as ah
import field_summarize as fs
import distance_angle_calculator as dac

env_path = "E:/InformationCenter/TestGDB.gdb"
table_name = "W2H"
table_name_2 = "H2W"
table_name_test = "W2H_TEST"
table_name_2_test = "H2W_TEST"
shp_name = "POINTS"  # 格网点（grid_id 、PX、PY）
QX_shp_name = "BOUND_17"  # 区县级别数据，面数据 （SSQ 名称、QBM 编码）
JD_shp_name = "BOUND_191"  # 街道级别数据，面数据 （SSJ 名称、JBM 编码）
field_name_distance = "DISTANCE"  # 添加的距离字段名字
field_name_angle = "ANGLE"
field_name_gid = "grid_id"  #
field_name_tpw = "GRID_ID_W"  # 表格中的两个待求距离的网格点的ID之一
field_name_tph = "GRID_ID_H"  # 表格中的两个待求距离的网格点的ID之一
field_name_sge = "Shape"  # 点要素图层中的图形字段
field_px = "PX"
field_py = "PY"
point_dict = {}
field_county_id = "QBM"
director_span = 2 * math.pi / 16.0


# 获取程序运行时间
def get_run_time(function):
    start_time = time.time()
    function()
    end_time = time.time()
    return end_time - start_time


def main():
    print "main start"
    ah.set_env(env_path, True)
    in_table = table_name
    # 计算H2W表格中的距离及角度
    dac.calculate(in_table,
                  {"grid_table": "POINTS", "x": "PX", "y": "PY", "id": "grid_id", "tpw": "GRID_ID_W", "tph": "GRID_ID_H"},
                  ["d", "w2h"])

    # 计算W2H表格中的距离及角度
    # dac.calculate("W2H",
    #               {"grid_table": "POINTS", "x": "PX", "y": "PY", "id": "grid_id", "tpw": "GRID_ID_W",
    #                "tph": "GRID_ID_H"},
    #               ["d", "w2h"])

    # 添加距离字段及角度字段，16方向分级
    my_new_fields = ["N"] + ["Distance_" + str(n) for n in xrange(1, 17)] + ["Volume_" + str(n) for n in xrange(1, 17)]
    fs.summary_16director("W_QBM", "QBM", [field_name_angle, field_name_distance, "WORK_NUM"], my_new_fields, in_table, QX_shp_name, "_W2H_DS_16")

    # 网格距离分级
    # WG_summary_dict = create_summary_dict(ah.get_rows(shp_name), field_name_gid)
    # d_c = [0, 2000, 4000, 6000, 10000, "inf"]
    # my_new_fields = ["A_" + str(d_c[i]) + "_" + str(d_c[i + 1]) for i in xrange(len(d_c)-1)]
    # fs.summary_distance(field_name_tph, field_name_gid, ["DISTANCE", "HOME_NUM"],
    #                     my_new_fields, WG_summary_dict, in_table, shp_name, "_H2W_DS")

    # jd_summary_dict = create_summary_dict(ah.get_rows(JD_shp_name), "JBM")
    # fs.summary_distance("JBM", "JBM", ["DISTANCE", "HOME_NUM"],
    #                     ["AVER_DISTANCE", "NUM_DISTANCE"], jd_summary_dict, in_table, JD_shp_name, "_H2W_DS")

    my_new_fields = ["A_420113", "A_420102", "A_420103", "A_420104", "A_420105", "A_420106", "A_420107",
                     "A_420111", "A_420112", "A_420114", "A_420115", "A_420116", "A_420117", "A_420118",
                     "A_420119", "A_420120", "A_420121"]
    fs.summary_workplace_17("GRID_ID_H", field_name_gid, ["WORK_NUM", "W_QBM"],
                            my_new_fields, in_table, shp_name, "_W2H_workplace")

    print "main done"
if __name__ == "__main__":
    print "main get time"
    print get_run_time(main)
