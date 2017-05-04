# -*- coding: UTF-8 -*-
import arcpy
import math

current_env_path = ""


# 根据路径及名字获取游标
def get_rows(name):
    print "get search cursor:", name
    return arcpy.SearchCursor(name)


# 获取可用于更新的游标
def get_update_rows(name):
    print "get update cursor:", name
    return arcpy.UpdateCursor(name)


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
    print "add:", field_type, " type field", field_name, "to table", table_name


def set_env(env_path, overwrite=True):
    print "set env:", env_path
    arcpy.env.workspace = env_path
    arcpy.env.overwriteOutput = overwrite
    global current_env_path
    current_env_path = env_path


def copy_feature(feature_name, env_path, describe):
    arcpy.FeatureClassToFeatureClass_conversion(feature_name, env_path, feature_name + describe)
    print "copy done", feature_name + describe
    return feature_name + describe


# 根据表格名字获取指定字段为主码的dict
def create_summary_dict(table_name, summary_field):
    rows = get_rows(table_name)
    summary_dict = {}
    for row in rows:
        summary_id = row.getValue(summary_field)
        summary_dict[summary_id] = {}
    return summary_dict


# 字段计算方法
# 工作空间中的表格名字 table_name
# 处理函数的列表 functions
# 处理结果字段名字的列表 result_fields
# 辅助的变量 aux
def calculate_fields(table_name, functions, result_fields, field_type="DOUBLE"):
    # 定义一个对rows迭代运用函数的迭代方法
    def calculator_rows(rows, function, result_field_name):
        for row in rows:
            result = function(row)
            add_field_value(result, result_field_name, row, rows)
    # table_rows = get_update_rows(t_name)
    for f, r in zip(functions, result_fields):
        print "on processing ", f.__name__
        # table_rows.reset()
        add_field(r, field_type, table_name)
        table_rows = get_update_rows(table_name)
        calculator_rows(table_rows, f, r)
        del table_rows


# 字段汇总类
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
        new_copy_table = copy_feature(self.out_table, current_env_path, self.describe)
        for new_field in new_fields:
            add_field(new_field, self.data_type, new_copy_table)
        point_edit_rows = get_update_rows(new_copy_table)
        for pe_row in point_edit_rows:
            pe_id = pe_row.getValue(self.out_summary_field)
            pe_obj = self.summary_dict[pe_id]
            for new_field in new_fields:
                # if pe_obj[new_field] != 0:
                add_field_value(pe_obj[new_field], new_field, pe_row, point_edit_rows)
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
        rows = get_rows(self.in_table)
        for row in rows:
            s_id = row.getValue(self.in_summary_field)
            if s_id:
                data = [row.getValue(d_f) for d_f in data_fields]
                summary_function(self.summary_dict[s_id], new_fields, data)
        if end_process_func:
            end_process_func[0](self.summary_dict)
        self.update(new_fields)

