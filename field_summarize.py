# -*- coding: UTF-8 -*-
import math
import arcgisHelper as ah
from arcgisHelper import SummaryGrid

director_span = 2 * math.pi / 16.0
# wg_shp_name = "POINTS"  # 格网点（grid_id 、PX、PY）网格汇总层次
# qx_shp_name = "BOUND_17"  # 区县级别数据，面数据 （SSQ 名称、QBM 编码）区县汇总层次
# jd_shp_name = "BOUND_191"  # 街道级别数据，面数据 （SSJ 名称、JBM 编码）街道汇总层次


def summary_16director(in_summary_field, out_summary_field, data_fields, new_fields, in_table, out_table, describe):
    def my_function(pid_obj, new_fields, data):
        if data[0] == -1:
            return
        angle = data[0] + 0.5 * director_span
        distance = data[1]
        volume = data[2]
        if angle >= 2 * math.pi:
            angle -= 2 * math.pi
        director = str(int(angle/director_span) + 1)
        # 计数
        pid_obj["N"] += 1
        # 距离累加
        pid_obj["Distance_" + director] += (distance * volume)
        # 流量累加
        pid_obj["Volume_" + director] += volume
        pass

    def calculate_aver(summary_dic):
        for pid_obj in summary_dic.values():
            for i in xrange(1, 17):
                volume = pid_obj["Volume_" + str(i)]
                if volume == 0:
                    pid_obj["Distance_" + str(i)] = 0
                else:
                    pid_obj["Distance_" + str(i)] /= volume
    summary_dict = ah.create_summary_dict(out_table, out_summary_field)
    sg = SummaryGrid(in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe)
    sg.summary(data_fields, new_fields, my_function, calculate_aver)


def summary_class_distance(in_summary_field, out_summary_field, data_fields, new_fields, in_table, out_table, describe):
    def my_function(pid_obj, fields, data):
        distance = data[0]
        num = data[1]
        for new_field in fields:
            l, r = [float(s) for s in new_field.split("_")[1:]]
            if l <= distance < r:
                pid_obj[new_field] += num
                break

    summary_dict = ah.create_summary_dict(out_table, out_summary_field)
    sg = SummaryGrid(in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe)
    sg.summary(data_fields, new_fields, my_function)


def summary_distance(in_summary_field, out_summary_field, data_fields, new_fields, in_table, out_table, describe):
    def my_function(pid_obj, fields, data):
        distance = data[0]
        num = data[1]
        pid_obj["NUM_DISTANCE"] += num
        pid_obj["AVER_DISTANCE"] += distance * num

    def calculate_aver(summary_dic):
        for pid_obj in summary_dic.values():
            if pid_obj["NUM_DISTANCE"] == 0:
                pid_obj["AVER_DISTANCE"] = 0
            else:
                pid_obj["AVER_DISTANCE"] /= pid_obj["NUM_DISTANCE"]

    summary_dict = ah.create_summary_dict(out_table, out_summary_field)
    sg = SummaryGrid(in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe)
    sg.summary(data_fields, new_fields, my_function, calculate_aver)


def summary_workplace_17(in_summary_field, out_summary_field, data_fields, new_fields, in_table, out_table, describe):
    def my_function(pid_obj, fields, data):
        num = data[0]
        w_qbm = data[1]
        if w_qbm:
            pid_obj["A_" + w_qbm] += num

    summary_dict = ah.create_summary_dict(out_table, out_summary_field)
    sg = SummaryGrid(in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe)
    sg.summary(data_fields, new_fields, my_function)
