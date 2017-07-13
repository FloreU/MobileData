# -*- coding: UTF-8 -*-
# 生成各个属性工作日、均值均值时间线
import arcpy
import sys
import time
from statistics import summary
from statistics import var_access

reload(sys)
sys.setdefaultencoding('utf-8')

# 统一属性
tmp_var_dir = "E:/InformationCenter/MobileData/tmp_var/"
date_filed = "TIME_DUR"
region_id_field = "GRID_ID"
template_table = "TIME_LINE_TEMPLATE"
time_points = ["09:00:00", "17:00:00"]
year_month = "2016_06"

work_day = [1, 2, 3,
            6, 7, 8, 9, 10,
            13, 14, 15, 16, 17,
            20, 21, 22, 23, 24,
            27, 28, 29, 30]
rest_day = [4,
            11, 12,
            18, 19,
            25, 26]
# work_day = [1, 2]
# rest_day = [4, 11]
# 年龄——时刻表
age_gdb = "E:/InformationCenter/Time_Age.gdb"
sum_age_gdb = "E:/InformationCenter/SUM_AGE.gdb"
age_field_list = ["AGE_15_19", "AGE_20_24", "AGE_25_29", "AGE_30_34", "AGE_35_39",
                  "AGE_40_44", "AGE_44_49", "AGE_49_91", "AGE_OTHER", "NUM_ALL"]
# 性别——时刻表
sex_gdb = "E:/InformationCenter/Time_Sex.gdb"
sum_sex_gdb = "E:/InformationCenter/SUM_SEX.gdb"
sex_field_list = ["NUM_MALE", "NUM_FEMALE", "NUM_OTHER", "NUM_ALL"]

curr_type = "AGE"
if curr_type == "SEX":
    c_gdb = sex_gdb
    c_sum_gdb = sum_sex_gdb
    c_field_list = sex_field_list
elif curr_type == "AGE":
    c_gdb = age_gdb
    c_sum_gdb = sum_age_gdb
    c_field_list = age_field_list
else:
    print ("type error!")
    sys.exit()

print("前期导入 -- 100%")


def create_name_list(prefix, curr_type, year_month, day_list):
    name_list = []
    for day in day_list:
        if day < 10:
            str_day = "0" + str(day)
        else:
            str_day = str(day)
        tmp_name = prefix + "_" + curr_type + "_" + year_month + "_" + str_day
        name_list.append(tmp_name)
    return name_list


def find_time48_index(time_str):
    time_hms = time_str.split(" ")[1]
    index = int(time_hms[0:2]) * 2
    if time_hms[3:5] == "30":
        index = index + 1
    return index - 1


def create_0_arr(num):
    array = []
    for i in range(num):
        array.append(0)
    return array


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


try:
    arcpy.env.workspace = c_gdb
    arcpy.env.overwriteOutput = True
    work_day_table = create_name_list("D_GRID", curr_type, year_month, work_day)
    rest_day_table = create_name_list("D_GRID", curr_type, year_month, rest_day)
    work_rest_day_table = {"WORK": work_day_table, "REST": rest_day_table}  # 工作日休息日对应表格
    all_result = {}
    for day_type in work_rest_day_table:
        print(day_type)
        cur_day_table = work_rest_day_table[day_type]
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
        all_result[day_type] = cur_day_result_obj
    var_access.save_var(all_result, (tmp_var_dir + curr_type + "_time_line.pkl"))

    create_time_line_table(c_sum_gdb, template_table, region_id_field)

    arcpy.env.workspace = c_sum_gdb
    arcpy.env.overwriteOutput = True

    all_result = var_access.load_var((tmp_var_dir + curr_type + "_time_line.pkl"))
    result_table_list = []
    for day_type in work_rest_day_table:
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
                    field_value = tmp_result[obj_id][i] / len(work_rest_day_table[day_type])
                    row.setValue(field_name, field_value)
                insert_cur.insertRow(row)
                count += 1
                if count % 1000 == 0:
                    print(time_line_table_name + "-" + str(count))
            result_table_list.append(time_line_table_name)


except Exception as err:
    print(err.args[0])
