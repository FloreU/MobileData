# -*- coding: UTF-8 -*-
import time
import math
import arcgisHelper as ah
import field_summarize as fs
import distance_angle_calculator as dac

env_path = "C:/MData/TestGDB.gdb"
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


class SummaryGrid(object):
    def __init__(self, in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe):
        self.in_table = in_table
        self.out_table = out_table
        self.summary_dict = summary_dict
        self.in_summary_field = in_summary_field
        self.out_summary_field = out_summary_field
        self.describe = describe

    def update(self, new_fields):
        new_copy_table = ah.copy_feature(self.out_table, env_path, self.describe)
        for new_field in new_fields:
            ah.add_field(new_field, "DOUBLE", new_copy_table)
        point_edit_rows = ah.get_update_rows(new_copy_table)
        for pe_row in point_edit_rows:
            pe_id = pe_row.getValue(self.out_summary_field)
            pe_obj = self.summary_dict[pe_id]
            for new_field in new_fields:
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


# 获取程序运行时间
def get_run_time(function):
    start_time = time.time()
    function()
    end_time = time.time()
    return end_time - start_time


# 主函数，汇总
# out_summary_field 在输出表格中汇总字段的名称，通常是表格的主码，通常和in_summary_field字段相同，但是也要看及具体数据
# in_summary_field 在输入表格或待汇总表格中，需要汇总的字段名称 （网格、街道、区）
#
def summary_test(in_summary_field, out_summary_field, data_fields, new_fields, summary_dict, in_table, out_table, describe):
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


def create_summary_dict(rows, summary_field):  # 最终数据形式的中间结果所存储的字典
    summary_dict = {}
    for row in rows:
        summary_id = row.getValue(summary_field)
        summary_dict[summary_id] = {}
    return summary_dict


def main():
    print "main start"
    ah.set_env(env_path, True)
    in_table = table_name_2_test
    # 计算H2W表格中的距离及角度
    dac.calculate(in_table,
                  {"grid_table": "POINTS", "x": "PX", "y": "PY", "id": "grid_id", "tpw": "GRID_ID_W", "tph": "GRID_ID_H"},
                  ["d", "h2w"])

    # 计算W2H表格中的距离及角度
    # dac.calculate("W2H",
    #               {"grid_table": "POINTS", "x": "PX", "y": "PY", "id": "grid_id", "tpw": "GRID_ID_W",
    #                "tph": "GRID_ID_H"},
    #               ["d", "w2h"])

    # 添加距离字段及角度字段，16方向分级
    qx_summary_dict = create_summary_dict(ah.get_rows(QX_shp_name), "QBM")
    my_new_fields = ["N"] + ["Distance_" + str(n) for n in xrange(1, 17)] + ["Volume_" + str(n) for n in xrange(1, 17)]
    fs.summary_16director("H_QBM", "QBM", [field_name_angle, field_name_distance, "HOME_NUM"], my_new_fields, qx_summary_dict, in_table, QX_shp_name, "_H2W_DS_16")



    # 网格距离分级
    # WG_summary_dict = create_summary_dict(ah.get_rows(shp_name), field_name_gid)
    # d_c = [0, 2000, 4000, 6000, 10000, "inf"]
    # my_new_fields = ["A_" + str(d_c[i]) + "_" + str(d_c[i + 1]) for i in xrange(len(d_c)-1)]
    # fs.summary_distance(field_name_tph, field_name_gid, ["DISTANCE", "HOME_NUM"],
    #                     my_new_fields, WG_summary_dict, in_table, shp_name, "_H2W_DS")

    # jd_summary_dict = create_summary_dict(ah.get_rows(JD_shp_name), "JBM")
    # fs.summary_distance("JBM", "JBM", ["DISTANCE", "HOME_NUM"],
    #                     ["AVER_DISTANCE", "NUM_DISTANCE"], jd_summary_dict, in_table, JD_shp_name, "_H2W_DS")

    wg_summary_dict = create_summary_dict(ah.get_rows(shp_name), field_name_gid)
    my_new_fields = ["A_420113", "A_420102", "A_420103", "A_420104", "A_420105", "A_420106", "A_420107",
                     "A_420111", "A_420112", "A_420114", "A_420115", "A_420116", "A_420117", "A_420118",
                     "A_420119", "A_420120", "A_420121"]
    fs.summary_workplace_17("GRID_ID_W", field_name_gid, ["HOME_NUM", "H_QBM"],
                            my_new_fields, wg_summary_dict, in_table, shp_name, "_H2W_workplace")

    print "main done"
if __name__ == "__main__":
    print "main get time"
    print get_run_time(main)
