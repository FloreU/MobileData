# -*- coding: UTF-8 -*-
# 生成各个属性每日
import sys

import arcpy

from statistics import var_access
from timeseriesLib import timeseries

reload(sys)
sys.setdefaultencoding('utf-8')

# 统一属性
tmp_var_dir = "E:/InformationCenter/MobileData/tmp_var/"
date_filed = "TIME_DUR"
region_id_field = "GRID_ID"
template_table = "TIME_LINE_TEMPLATE"
change_template_table = "CHANGE_TIME_LINE_TEMPLATE"
year_month = "2016_06"

all_day = [1, 2, 3, 4,
           6, 7, 8, 9, 10, 11, 12,
           13, 14, 15, 16, 17, 18, 19,
           20, 21, 22, 23, 24, 25, 26,
           27, 28, 29, 30]
# all_day=[1,2]
# 年龄——时刻表
age_gdb = "E:/InformationCenter/Time_Age.gdb"
sum_age_gdb = "E:/InformationCenter/SUM_AGE.gdb"
time_line_gdb = "E:/InformationCenter/AGETIMELINE.gdb"
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
try:
    arcpy.env.workspace = c_gdb
    arcpy.env.overwriteOutput = True
    day_table_list = timeseries.create_name_list("D_GRID", curr_type, year_month, all_day)
    timeseries.create_time_line_table(time_line_gdb, template_table, region_id_field)
    result_tables = []
    for day_table in day_table_list:
        day_result_obj = timeseries.get_one_day_time_series(day_table, c_field_list, region_id_field, date_filed)
        time_line_tables = timeseries.insert_one_day_time_line_table(day_result_obj, day_table, c_field_list,
                                                                     time_line_gdb, template_table, region_id_field)
        result_tables = result_tables + time_line_tables
except Exception as err:
    print(err.args[0])
