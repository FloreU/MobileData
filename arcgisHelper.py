# -*- coding: UTF-8 -*-
import arcpy
import math


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
    arcpy.AddField_management(table_name, field_name, field_type, field_is_nullable="NON_NULLABLE")
    print "add:", field_type, " type field", field_name, "to table", table_name


def set_env(env_path, overwrite=True):
    print "set env:", env_path
    arcpy.env.workspace = env_path
    arcpy.env.overwriteOutput = overwrite


def copy_feature(feature_name, env_path, describe):
    arcpy.FeatureClassToFeatureClass_conversion(feature_name, env_path, feature_name + describe)
    print "copy done", feature_name + describe
    return feature_name + describe
