# -*- coding: UTF-8 -*-
import math
import arcgisHelper as ah

env_path = "C:/MData/TestGDB.gdb"
director_span = 2 * math.pi / 16.0
WG_shp_name = "POINTS"  # 格网点（grid_id 、PX、PY）网格汇总层次
QX_shp_name = "BOUND_17"  # 区县级别数据，面数据 （SSQ 名称、QBM 编码）区县汇总层次
JD_shp_name = "BOUND_191"  # 街道级别数据，面数据 （SSJ 名称、JBM 编码）街道汇总层次


class SummaryGrid(object):
    def __init__(self, in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe, data_type="DOUBLE"):
        self.in_table = in_table
        self.out_table = out_table
        self.summary_dict = summary_dict
        self.in_summary_field = in_summary_field
        self.out_summary_field = out_summary_field
        self.describe = describe
        self.data_type = data_type

    def update(self, new_fields):
        new_copy_table = ah.copy_feature(self.out_table, env_path, self.describe)
        for new_field in new_fields:
            ah.add_field(new_field, self.data_type, new_copy_table)
        point_edit_rows = ah.get_update_rows(new_copy_table)
        for pe_row in point_edit_rows:
            pe_id = pe_row.getValue(self.out_summary_field)
            pe_obj = self.summary_dict[pe_id]
            for new_field in new_fields:
                if pe_obj[new_field] != 0:
                    ah.add_field_value(pe_obj[new_field], new_field, pe_row, point_edit_rows)
        del point_edit_rows

    # summary_field 需要汇总的字段；
    # data_fields 数据字段；
    # new_field 汇总结果新建字段
    def summary(self, data_fields, new_fields, summary_function, *end_process_func):
        def init_pid_dict(init_value):
            for v in self.summary_dict.itervalues():
                for new_field in new_fields:
                    v[new_field] = init_value
        init_pid_dict(0.0)
        rows = ah.get_rows(self.in_table)
        for row in rows:
            s_id = row.getValue(self.in_summary_field)
            if s_id:
                data = [row.getValue(d_f) for d_f in data_fields]
                summary_function(self.summary_dict[s_id], new_fields, data)
        if end_process_func:
            end_process_func[0](self.summary_dict)
        self.update(new_fields)


def summary_16director(in_summary_field, out_summary_field, data_fields, new_fields, summary_dict, in_table, out_table, describe):
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

    sg = SummaryGrid(in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe)
    sg.summary(data_fields, new_fields, my_function, calculate_aver)


def summary_class_distance(in_summary_field, out_summary_field, data_fields, new_fields, summary_dict, in_table, out_table, describe):
    def my_function(pid_obj, fields, data):
        distance = data[0]
        num = data[1]
        for new_field in fields:
            l, r = [float(s) for s in new_field.split("_")[1:]]
            if l <= distance < r:
                pid_obj[new_field] += num
                break
    sg = SummaryGrid(in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe)
    sg.summary(data_fields, new_fields, my_function)


def summary_distance(in_summary_field, out_summary_field, data_fields, new_fields, summary_dict, in_table, out_table, describe):
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
    sg = SummaryGrid(in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe)
    sg.summary(data_fields, new_fields, my_function, calculate_aver)


def summary_workplace_17(in_summary_field, out_summary_field, data_fields, new_fields, summary_dict, in_table, out_table, describe):
    def my_function(pid_obj, fields, data):
        num = data[0]
        w_qbm = data[1]
        if w_qbm:
            pid_obj["A_" + w_qbm] += num

    sg = SummaryGrid(in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe)
    sg.summary(data_fields, new_fields, my_function)
