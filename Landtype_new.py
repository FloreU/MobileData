# -*- coding: UTF-8 -*-
import arcpy
import os

base_path = "C:/Workspace/"

raw_type_dict = {
    "武昌": ["武昌区", "洪山区"],
    "汉口": ["江汉区", "江岸区"],
    "汉阳": ["汉阳区", "黄陂区"]
}
added_field_name = "DLDM1"
type_field_dict = ["SSQ", "行政区域"]
other_name = "其他地类"


# 给某一行对象添加一属性值
def add_field_value(value, field_name, row, cursor):
    row.setValue(field_name, value)
    cursor.updateRow(row)


def create_type_dict(raw_dict):
    return {child: prt for prt in raw_dict.keys() for child in raw_dict[prt]}


def get_rows(name):
    return arcpy.SearchCursor(name)


def get_update_rows(name):
    return arcpy.UpdateCursor(name)


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
    arcpy.AddField_management(table_name, field_name, field_type)


def main_process(name, type_dict, type_field_name):
    add_field(added_field_name, "TEXT", name)
    rows = get_update_rows(name)
    for row in rows:
        child_type = row.getValue(type_field_name).encode("utf8")
        parent_type = other_name
        if child_type in type_dict.keys():
            parent_type = type_dict[child_type]
        add_field_value(parent_type, added_field_name, row, rows)


def main():
    type_dict = create_type_dict(raw_type_dict)
    for env_path in os.listdir(base_path):
        if env_path.endswith(".mdb") or env_path.endswith(".gdb"):
            arcpy.env.workspace = base_path + env_path
            feature_classes = arcpy.ListFeatureClasses()
            for feature_name in feature_classes:
                print "process on", env_path, feature_name
                feature_fields_list = arcpy.ListFields(feature_name)
                for tp in type_field_dict:
                    if tp in [n.aliasName.encode("utf8") for n in feature_fields_list]:
                        main_process(feature_name, type_dict, tp)
                        break

if __name__ == '__main__':
    main()
