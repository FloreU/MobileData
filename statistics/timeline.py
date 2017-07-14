# -*- coding: UTF-8 -*-
# 生成时间线所需
import os
import arcpy
import sys
import time

reload(sys)
sys.setdefaultencoding('utf-8')


# 将数据库中单张表输出为excel
# in_table：输入数据库表的名称
# out_xls：输出xls文件的路径（包含文件名）
def output_xls(in_table, out_xls):
    try:
        arcpy.TableToExcel_conversion(in_table, out_xls)
        return 1
    except Exception as err:
        print(err.args[0])
        return 0


# 将数据库中多张表输出为excel
# in_table：输入数据库表的名称列表
# out_xls：输出xls文件存放的文件夹路径
def output_xls_batch(in_table_list, out_path):
    xls_file_list = []
    for table in in_table_list:
        out_name = table.split("/")[-1]
        out_name = out_name.split("\\")[-1]
        xls_path = out_path + "/" + out_name + ".xls"
        output_xls(table, xls_path)
        print(xls_path)
        xls_file_list.append(xls_path)
    return xls_file_list


# 将数据库中所有表输出为excel
# in_table：输入数据库表路径
# out_xls：输出xls文件存放的文件夹路径
def output_gdb_xls(in_gdb, out_path):
    old_workspace = arcpy.env.workspace
    arcpy.env.workspace = in_gdb
    table_list = arcpy.ListTables()
    gdb_name = in_gdb.split("/")[-1]
    gdb_name = gdb_name.split("\\")[-1]
    gdb_name = gdb_name.split(".")[0]
    out_path = out_path + "/" + gdb_name
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    xls_file_list = output_xls_batch(table_list, out_path)
    arcpy.env.workspace = old_workspace
    return xls_file_list


# 根据输入的前缀、种类、年月、日期列表生成名称列表
# prefix：输入前缀
# current_type：数据种类
# year_month：年月
# day_list：日期列表
def create_name_list(prefix, current_type, year_month, day_list):
    name_list = []
    for day in day_list:
        if day < 10:
            str_day = "0" + str(day)
        else:
            str_day = str(day)
        tmp_name = prefix + "_" + current_type + "_" + year_month + "_" + str_day
        name_list.append(tmp_name)
    return name_list


# 获得当前时间点在48个时间点中的索引位置（00:30:00-24:00:00）
# time_str：输入时间字符串yyyy-MM-dd hh:mm:ss
def find_time48_index(time_str):
    time_hms = time_str.split(" ")[1]
    index = int(time_hms[0:2]) * 2
    if time_hms[3:5] == "30":
        index = index + 1
    return index - 1


# 生成指定长度的一维0数组
# num：数组长度
def create_0_arr(num):
    array = []
    for i in range(num):
        array.append(0)
    return array


# 生成48个时刻当中对应时刻的属性列名
# num：48个时刻中的索引
# 生成TL_00_30样式的属性名
def time_line_field(num):
    cur_i = num + 1
    remainder = cur_i % 2
    quotient = cur_i / 2
    if quotient < 10:
        q_str = "0" + str(quotient)
    else:
        q_str = str(quotient)
    if remainder == 0:
        r_str = "00"
    else:
        r_str = "30"
    tl_field_name = "TL_" + q_str + "_" + r_str
    return tl_field_name


# 生成时间线属性表
# out_path：输出gdb路径
# out_table：输出表格名称
# id_field：时间线表格中表示格网id的属性段
def create_time_line_table(out_path, out_table, id_field):
    arcpy.CreateTable_management(out_path, out_table, "", "")
    out_template = out_path + "/" + out_table
    arcpy.AddField_management(out_template, id_field, "LONG")
    time_line = []
    for i in range(48):
        tl_field_name = time_line_field(i)
        time_line.append(tl_field_name)
    for time_index in time_line:
        arcpy.AddField_management(out_template, time_index, "DOUBLE")
    return out_template
