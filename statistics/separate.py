# -*- coding: UTF-8 -*-
import re
import arcpy
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def attribute_unique(in_feature, field_name):
    start_time = time.time()
    unique_val_list = []
    in_feature_cur = arcpy.SearchCursor(in_feature)
    for row in in_feature_cur:
        filed_value = row.getValue(field_name)
        if filed_value not in unique_val_list:
            unique_val_list.append(filed_value)
    end_time = time.time()
    del in_feature_cur
    print("耗时: {0} s".format(end_time - start_time))
    return unique_val_list


def separate_table_day(table_name, date_filed, day_value, in_path="", out_path=""):
    expression = date_filed + " LIKE '" + day_value + "%'"
    new_table_name = out_path + "D_" + table_name + "_" + re.sub(r'\W', "_", day_value)
    table_name = in_path + table_name
    arcpy.TableToTable_conversion(table_name, arcpy.env.workspace, new_table_name, expression)
    return new_table_name


def separate_table_days(table_name, date_filed, day_list=None, in_path="", out_path=""):
    if day_list is None:
        print("分拆表格 - 获取唯一日期...")
        time_list = attribute_unique(in_path + table_name, date_filed)
        day_list = []
        for every_time in time_list:
            time_array = every_time.split(" ")
            if time_array[0] not in day_list:
                day_list.append(time_array[0])
        print("分拆表格 - 获取唯一日期 -- 100%")
    table_name_list = []
    day_count = len(day_list)
    count = 0.0
    print("分拆表格 - 分拆中 -- 0%")
    for every_day in day_list:
        new_table_name = separate_table_day(table_name, date_filed, every_day, in_path, out_path)
        table_name_list.append(new_table_name)
        count += 1
        print("分拆表格 - 分拆中 -- {:.2f}%".format(count / day_count * 100))
    return table_name_list

