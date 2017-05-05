# -*- coding: UTF-8 -*-
import arcpy
import sys

from statistics import summary
from statistics import var_access

reload(sys)
sys.setdefaultencoding('utf-8')

# 统一属性
tmp_var_dir = "E:/InformationCenter/MobileData/tmp_var"
date_filed = "TIME_DUR"
region_id_field = "GRID_ID"
time_points = ["09:00:00", "17:00:00"]
year_month = "2016-06-"
work_day = [1, 2, 3,
            6, 7, 8, 9, 10,
            13, 14, 15, 16, 17,
            20, 21, 22, 23, 24,
            27, 28, 29, 30]
template_table = "SUM_TEMPLATE"
curr_type = "Sex"
# 年龄——时刻表
age_gdb = "E:/InformationCenter/Time_Age.gdb"
sum_age_gdb = "E:/InformationCenter/SUM_AGE.gdb"
age_var_file_pkl = tmp_var_dir + "/DayTableAge.pkl"
age_field_list = ["AGE_15_19", "AGE_20_24", "AGE_25_29", "AGE_30_34", "AGE_35_39",
                  "AGE_40_44", "AGE_44_49", "AGE_49_91", "AGE_OTHER", "NUM_ALL"]
# 性别——时刻表
sex_gdb = "E:/InformationCenter/Time_Sex.gdb"
sum_sex_gdb = "E:/InformationCenter/SUM_SEX.gdb"
sex_var_file_pkl = tmp_var_dir + "/DayTableSex.pkl"
sex_field_list = ["NUM_MALE", "NUM_FEMALE", "NUM_OTHER", "NUM_ALL"]

if curr_type == "Sex":
    c_gdb = sex_gdb
    c_sum_gdb = sum_sex_gdb
    c_var_file = sex_var_file_pkl
    c_field_list = sex_field_list
elif curr_type == "Age":
    c_gdb = age_gdb
    c_sum_gdb = sum_age_gdb
    c_var_file = age_var_file_pkl
    c_field_list = age_field_list
else:
    print ("type error!")
    sys.exit()

arcpy.env.workspace = c_sum_gdb
print("前期导入 -- 100%")
try:
    arcpy.env.overwriteOutput = True
    table_name_list = var_access.load_var(c_var_file)
    out_template = summary.create_summary_model_table1(c_sum_gdb, template_table, region_id_field, c_field_list)
    print("模板创建 -- 100%")
    day_num = len(work_day)
    sum_table_list = []
    work_day_result = {}
    for table in table_name_list:
        name_array = table.split("_")
        table_date = name_array[-3] + "-" + name_array[-2] + "-" + name_array[-1]
        if int(name_array[-1]) not in work_day:
            continue
        for time_point in time_points:
            this_time = table_date + " " + time_point
            expression = date_filed + " = '" + this_time + "'"
            work_day_result = summary.field_calculate2(
                c_gdb + "／" + table, region_id_field,
                c_field_list, time_point, expression, work_day_result
            )
            print(table+"_"+time_point)
    work_day_result = summary.calculate_average2(work_day_result, day_num)

    for time_point in time_points:
        sum_work_day_time_point_table = "SUM_" + curr_type + "_" + time_point.replace(":", "_")
        arcpy.CreateTable_management(c_sum_gdb, sum_work_day_time_point_table, out_template, "")
        summary.save_table2(sum_work_day_time_point_table, work_day_result, region_id_field, time_point)
        sum_table_list.append(sum_work_day_time_point_table)
        print(sum_work_day_time_point_table)
except Exception as err:
    print(err.args[0])
