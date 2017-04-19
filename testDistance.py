# -*- coding: UTF-8 -*-
import arcpy
import time
import math

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
        for new_field in new_fields:
            add_field(new_field, "DOUBLE", self.out_table)
        point_edit_rows = get_update_rows(self.copy_feature(self.out_table))
        for pe_row in point_edit_rows:
            pe_id = pe_row.getValue(self.out_summary_field)
            pe_obj = self.summary_dict[pe_id]
            for new_field in new_fields:
                add_field_value(pe_obj[new_field], new_field, pe_row, point_edit_rows)
        del point_edit_rows

    def copy_feature(self, feature_name):
        arcpy.FeatureClassToFeatureClass_conversion(feature_name, env_path, feature_name + self.describe)
        return feature_name + self.describe

    # summary_field 需要汇总的字段；
    # data_fields 数据字段；
    # new_field 汇总结果新建字段
    def summary(self, data_fields, new_fields, summary_function, *end_process_func):
        def init_pid_dict(init_value):
            for v in self.summary_dict.itervalues():
                for new_field in new_fields:
                    v[new_field] = init_value
        init_pid_dict(0.0)
        rows = get_rows(self.in_table)
        for row in rows:
            s_id = row.getValue(self.in_summary_field)
            if s_id:
                data = [row.getValue(d_f) for d_f in data_fields]
                summary_function(self.summary_dict[s_id], new_fields, data)
        if end_process_func:
            end_process_func[0](self.summary_dict)
        self.update(new_fields)


# 根据路径及名字获取游标
def get_rows(name):
    return arcpy.SearchCursor(name)


# 获取可用于更新的游标
def get_update_rows(name):
    return arcpy.UpdateCursor(name)


def create_point_dict(rows):
    point_id_dict = {}
    for row in rows:
        point_id = row.getValue(field_name_gid)
        point_x = row.getValue(field_px)
        point_y = row.getValue(field_py)
        point_id_dict[point_id] = {field_px: point_x, field_py: point_y}
    return point_id_dict


# 根据两点的id及字典获取距离
def get_angle(id1, id2, point_dict):
    point1 = point_dict[id1]
    point2 = point_dict[id2]
    p1_x = point1[field_px]
    p2_x = point2[field_px]
    p1_y = point1[field_py]
    p2_y = point2[field_py]
    dtx = p2_x - p1_x
    dty = p2_y - p1_y
    return angle(dty, dtx)


def angle(dty, dtx):
    if dty == 0 and dtx == 0:
        return -1
    m_angle = math.atan2(dty, dtx)
    if m_angle < 0:
        m_angle += 2 * math.pi
    return m_angle


def get_distance(id1, id2, point_dict):
    point1 = point_dict[id1]
    point2 = point_dict[id2]
    return math.sqrt((point1[field_px] - point2[field_px]) ** 2+(point1[field_py] - point2[field_py]) ** 2)

# 根据条件搜索符合条件的要素集合
# def get_search_point(path, name, where_clause):
#     rows = arcpy.SearchCursor(path + name, where_clause)
#     for row in rows:
#         return row.getValue(field_name_sge)


# 给某一行对象添加一属性值
def add_field_value(value, field_name, row, cursor):
    row.setValue(field_name, value)
    cursor.updateRow(row)


# ·TEXT —名称或其他文本特性。
# ·FLOAT —特定范围内含小数值的数值。
# ·DOUBLE —特定范围内含小数值的数值。
# ·SHORT —特定范围内不含小数值的数值；编码值。
# ·LONG —特定范围内不含小数值的数值。
# ·DATE —日期和/或时间。
# ·BLOB —影像或其他多媒体。
# ·RASTER —栅格影像。
# ·GUID —GUID 值
def add_field(field_name, field_type, table_name):
    if field_name in arcpy.ListFields(table_name):
        arcpy.DeleteField_management(table_name, field_name)
    arcpy.AddField_management(table_name, field_name, field_type)


# 获取程序运行时间
def get_run_time(function):
    start_time = time.time()
    function()
    end_time = time.time()
    return end_time - start_time


# def s_f_test(pid_obj, new_field, summary_data, case_data):
#     pid_obj[new_field] += summary_data

# 主函数，汇总
# out_summary_field 在输出表格中汇总字段的名称，通常是表格的主码，通常和in_summary_field字段相同，但是也要看及具体数据
# in_summary_field 在输入表格或待汇总表格中，需要汇总的字段名称
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
        pid_obj["n"] += 1
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


def cac_angle_h2w(table_rows, point_dict):
    for row in table_rows:
        id1 = row.getValue(field_name_tph)
        id2 = row.getValue(field_name_tpw)
        angle = get_angle(id1, id2, point_dict)
        add_field_value(angle, field_name_angle, row, table_rows)


def cac_angle_w2h(table_rows, point_dict):
    for row in table_rows:
        id1 = row.getValue(field_name_tpw)
        id2 = row.getValue(field_name_tph)
        angle = get_angle(id1, id2, point_dict)
        add_field_value(angle, field_name_angle, row, table_rows)


def cac_distance(table_rows, point_dict):
    for row in table_rows:
        id1 = row.getValue(field_name_tpw)
        id2 = row.getValue(field_name_tph)
        distance = get_distance(id1, id2, point_dict)
        add_field_value(distance, field_name_distance, row, table_rows)


# 主函数
# 游标更新的问题还未解决
def execute_rows_update(p_dict, t_name, *functions):
    # table_rows = get_update_rows(t_name)
    for f in functions:
        print "on processing ", f.__name__
        # table_rows.reset()
        table_rows = get_update_rows(t_name)
        f(table_rows, p_dict)
        del table_rows


def create_summary_dict(rows, summary_field):  # 最终数据形式的中间结果所存储的字典
    summary_dict = {}
    for row in rows:
        summary_id = row.getValue(summary_field)
        summary_dict[summary_id] = {}
    return summary_dict


def main():
    arcpy.env.workspace = env_path
    in_summary_field = "H_QBM"
    out_summary_field = "QBM"
    in_table = table_name_2_test
    out_table = QX_shp_name
    # 添加距离字段及角度字段
    add_field(field_name_angle, "DOUBLE", in_table)
    add_field(field_name_distance, "DOUBLE", in_table)
    point_dict = create_point_dict(get_rows(shp_name))
    execute_rows_update(point_dict, in_table, cac_angle_h2w, cac_distance)
    QX_summary_dict = create_summary_dict(get_rows(QX_shp_name), out_summary_field)
    my_new_fields = ["n"] + ["Distance_" + str(n) for n in xrange(1, 17)] + ["Volume_" + str(n) for n in xrange(1, 17)]
    # def summary_test(summary_field, data_fields, new_fields, summary_dict, in_table, out_table):
    summary_test(in_summary_field, out_summary_field, [field_name_angle, field_name_distance, "HOME_NUM"], my_new_fields, QX_summary_dict, in_table, out_table, "H2W_DS")

print get_run_time(main)
