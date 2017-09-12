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
        if prefix is None:
            tmp_name = current_type + "_" + year_month + "_" + str_day
        else:
            tmp_name = prefix + "_" + current_type + "_" + year_month + "_" + str_day
        name_list.append(tmp_name)
    return name_list


# 根据Table列表获得对应日期
def get_real_date(table_name):
    name_list = table_name.split("_")
    real_date = name_list[-3] + "_" + name_list[-2] + "_" + name_list[-1]
    return real_date


def get_real_type(table_name):
    name_list = table_name.split("_")
    real_type = name_list[-4]
    return real_type


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


# 生成48个时刻当中对应时刻
# num：48个时刻中的索引
# 生成00_30样式的时刻
def index2time(num):
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
    time_str = q_str + "_" + r_str
    return time_str


# 生成48个时刻当中对应时刻的属性列名
# num：48个时刻中的索引
# 生成TL_00_30样式的属性名
def time_line_field(num):
    tl_field_name = "TL_" + index2time(num)
    return tl_field_name


# 生成47个时段当中对应时段的属性列名
# num：47个时刻中的索引
# 生成CTL_00_30_01_00样式的属性名
def change_time_line_field(num):
    ctl_field_name = "CTL_" + index2time(num) + "_" + index2time(num + 1)
    return ctl_field_name


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


# 生成时间线变化表（用于存储改变量-斜率以及变化率）
# out_path：输出gdb路径
# out_table：输出表格名称
# id_field：时间线表格中表示格网id的属性段
def create_change_time_line_table(out_path, out_table, id_field):
    arcpy.CreateTable_management(out_path, out_table, "", "")
    out_template = out_path + "/" + out_table
    arcpy.AddField_management(out_template, id_field, "LONG")
    time_line = []
    for i in range(47):
        tl_field_name = change_time_line_field(i)
        time_line.append(tl_field_name)
    for time_index in time_line:
        arcpy.AddField_management(out_template, time_index, "DOUBLE")
    return out_template


def sum_every_time_by_type(cur_day_table, c_field_list, region_id_field, date_filed, day_type):
    cur_day_result_obj = {}
    for field in c_field_list:
        cur_day_result_obj[field] = {}
    for day_table in cur_day_table:
        time1 = time.time()
        search_cur = arcpy.SearchCursor(day_table)
        print(day_table)
        count = 0.0
        for row in search_cur:
            obj_id = row.getValue(region_id_field)
            time_str = row.getValue(date_filed)
            id_48 = find_time48_index(time_str)
            for field in c_field_list:
                if obj_id not in cur_day_result_obj[field]:
                    tmp_filed_array = create_0_arr(48)
                    cur_day_result_obj[field][obj_id] = tmp_filed_array
                field_value = row.getValue(field)
                cur_day_result_obj[field][obj_id][id_48] += field_value
            count += 1
            if count % 1000 == 0:
                print(day_type + "-" + day_table + "-" + str(count))
        time2 = time.time()
        print((time2 - time1) / 60)
    return cur_day_result_obj


def sum_every_time(work_rest_day_table, c_field_list, region_id_field, date_filed):
    all_result = {}
    for day_type in work_rest_day_table:
        print(day_type)
        cur_day_table = work_rest_day_table[day_type]
        cur_day_result_obj = sum_every_time_by_type(cur_day_table, c_field_list, region_id_field, date_filed, day_type)
        all_result[day_type] = cur_day_result_obj
    return all_result


def insert_time_line_table(all_result, work_rest_day_table, c_field_list, c_sum_gdb, template_table, region_id_field):
    result_table_list = []
    for day_type in work_rest_day_table:
        day_num = len(work_rest_day_table[day_type])
        cur_day_result_obj = all_result[day_type]
        for field in c_field_list:
            tmp_result = cur_day_result_obj[field]
            time_line_table_name = "TL_" + day_type + "_" + field
            arcpy.CreateTable_management(c_sum_gdb, time_line_table_name, template_table, "")
            insert_cur = arcpy.InsertCursor(time_line_table_name)
            count = 0.0
            for obj_id in tmp_result:
                row = insert_cur.newRow()
                row.setValue(region_id_field, obj_id)
                for i in range(48):
                    field_name = time_line_field(i)
                    field_value = tmp_result[obj_id][i] / day_num
                    row.setValue(field_name, field_value)
                insert_cur.insertRow(row)
                count += 1
                if count % 1000 == 0:
                    print(time_line_table_name + "-" + str(count))
            result_table_list.append(time_line_table_name)
    return result_table_list


def insert_slope_time_line_table(all_result, work_rest_day_table, c_field_list, c_sum_gdb, template_table,
                                 region_id_field):
    result_table_list = []
    for day_type in work_rest_day_table:
        day_num = len(work_rest_day_table[day_type])
        cur_day_result_obj = all_result[day_type]
        for field in c_field_list:
            tmp_result = cur_day_result_obj[field]
            time_line_table_name = "STL_" + day_type + "_" + field
            arcpy.CreateTable_management(c_sum_gdb, time_line_table_name, template_table, "")
            insert_cur = arcpy.InsertCursor(time_line_table_name)
            count = 0.0
            for obj_id in tmp_result:
                row = insert_cur.newRow()
                row.setValue(region_id_field, obj_id)
                for i in range(47):
                    field_name = change_time_line_field(i)
                    field_value = (tmp_result[obj_id][i + 1] - tmp_result[obj_id][i]) / day_num
                    row.setValue(field_name, field_value)
                insert_cur.insertRow(row)
                count += 1
                if count % 1000 == 0:
                    print(time_line_table_name + "-" + str(count))
            result_table_list.append(time_line_table_name)
    return result_table_list


def insert_rate_time_line_table(all_result, work_rest_day_table, c_field_list, c_sum_gdb, template_table,
                                region_id_field):
    result_table_list = []
    for day_type in work_rest_day_table:
        cur_day_result_obj = all_result[day_type]
        for field in c_field_list:
            tmp_result = cur_day_result_obj[field]
            time_line_table_name = "RTL_" + day_type + "_" + field
            arcpy.CreateTable_management(c_sum_gdb, time_line_table_name, template_table, "")
            insert_cur = arcpy.InsertCursor(time_line_table_name)
            count = 0.0
            for obj_id in tmp_result:
                row = insert_cur.newRow()
                row.setValue(region_id_field, obj_id)
                for i in range(47):
                    field_name = change_time_line_field(i)
                    if tmp_result[obj_id][i] == 0:
                        field_value = (tmp_result[obj_id][i + 1] - tmp_result[obj_id][i]) / 0.01
                    else:
                        field_value = (tmp_result[obj_id][i + 1] - tmp_result[obj_id][i]) / tmp_result[obj_id][i]
                    row.setValue(field_name, field_value)
                insert_cur.insertRow(row)
                count += 1
                if count % 1000 == 0:
                    print(time_line_table_name + "-" + str(count))
            result_table_list.append(time_line_table_name)
    return result_table_list


def read_cluster(cluster_file_path, type_obj_id='int', type_obj_cluster='int'):
    r_cluster_obj = {}
    cluster_file = open(cluster_file_path, 'r')
    cluster_line = cluster_file.readlines()
    for line in cluster_line:
        line_a = line.split(",")
        obj_id_str = line_a[0]
        obj_cluster_str = line_a[1]
        if type_obj_id == 'int':
            obj_id = int(obj_id_str)
        elif type_obj_id == 'float':
            obj_id = float(obj_id_str)
        elif type_obj_id == 'string':
            obj_id = obj_id_str
        if type_obj_cluster == 'int':
            obj_cluster = int(obj_cluster_str)
        elif type_obj_cluster == 'float':
            obj_cluster = float(obj_cluster_str)
        elif type_obj_cluster == 'string':
            obj_cluster = obj_cluster_str
        r_cluster_obj[obj_id] = obj_cluster
    cluster_file.close()
    return r_cluster_obj


def set_cluster(cluster_table, cluster_file_path, region_id_field, cluster_field, type_obj_id='int',
                type_obj_cluster='int'):
    cluster_obj = read_cluster(cluster_file_path, type_obj_id, type_obj_cluster)
    if type_obj_cluster == 'int':
        arcpy.AddField_management(cluster_table, cluster_field, "LONG")
    elif type_obj_cluster == 'float':
        arcpy.AddField_management(cluster_table, cluster_field, "DOUBLE")
    elif type_obj_cluster == 'string':
        arcpy.AddField_management(cluster_table, cluster_field, "TEXT")
    update_cur = arcpy.UpdateCursor(cluster_table)
    for row in update_cur:
        obj_id = row.getValue(region_id_field)
        if obj_id in cluster_obj:
            row.setValue(cluster_field, cluster_obj[obj_id])
        else:
            row.setValue(cluster_field, None)
        update_cur.updateRow(row)
    return


def get_one_day_time_series(day_table, field_list, region_id_field, date_filed):
    cur_day_result_obj = {}
    for field in field_list:
        cur_day_result_obj[field] = {}

    time1 = time.time()
    search_cur = arcpy.SearchCursor(day_table)
    print(day_table)
    count = 0.0
    for row in search_cur:
        obj_id = row.getValue(region_id_field)
        time_str = row.getValue(date_filed)
        id_48 = find_time48_index(time_str)
        for field in field_list:
            if obj_id not in cur_day_result_obj[field]:
                tmp_filed_array = create_0_arr(48)
                cur_day_result_obj[field][obj_id] = tmp_filed_array
            field_value = row.getValue(field)
            cur_day_result_obj[field][obj_id][id_48] += field_value
        count += 1
        if count % 1000 == 0:
            print(day_table + "-" + str(count))
    time2 = time.time()
    print((time2 - time1) / 60)
    return cur_day_result_obj


def insert_one_day_time_line_table(day_result_obj, day_table, field_list, save_gdb, template_table, region_id_field):
    result_table = []
    for field in field_list:
        tmp_result = day_result_obj[field]
        real_date = get_real_date(day_table)
        real_type = get_real_type(day_table)
        time_line_table_name = "TL_" + real_type + "_" + field + "_" + real_date
        arcpy.CreateTable_management(save_gdb, time_line_table_name, save_gdb + "/" + template_table, "")
        insert_cur = arcpy.InsertCursor(save_gdb + "/" + time_line_table_name)
        count = 0.0
        for obj_id in tmp_result:
            row = insert_cur.newRow()
            row.setValue(region_id_field, obj_id)
            for i in range(48):
                field_name = time_line_field(i)
                field_value = tmp_result[obj_id][i]
                row.setValue(field_name, field_value)
            insert_cur.insertRow(row)
            count += 1
            if count % 1000 == 0:
                print(time_line_table_name + "-" + str(count))
        result_table.append(time_line_table_name)
    return result_table
