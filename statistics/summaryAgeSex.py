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
time_interval = ["09:00:00", "17:00:00"]
curr_type = "Sex"
# 年龄——时刻表
age_gdb = "E:/InformationCenter/Time_Age.gdb"
sum_age_gdb = "E:/InformationCenter/SUM_AGE.gdb"
age_var_file_pkl = tmp_var_dir + "DayTableAge.pkl"
age_field_list = ["AGE_15_19", "AGE_20_24", "AGE_25_29", "AGE_30_34", "AGE_35_39",
                  "AGE_40_44", "AGE_44_49", "AGE_49_91", "AGE_OTHER", "NUM_ALL"]
# 性别——时刻表
sex_gdb = "E:/InformationCenter/Time_Sex.gdb"
sum_sex_gdb = "E:/InformationCenter/SUM_SEX.gdb"
sex_var_file_pkl = tmp_var_dir + "DayTableSex.pkl"
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

arcpy.env.workspace = c_gdb
print("前期导入 -- 100%")
try:
    arcpy.env.overwriteOutput = True
    table_name_list = var_access.load_var(c_var_file)
    for table in table_name_list:
        name_array = table.split("_")
        table_date = name_array[-3] + "-" + name_array[-2] + "-" + name_array[-1]
        start_time = table_date + " " + time_interval[0]
        end_time = table_date + " " + time_interval[1]
        expression = date_filed + " >= '" + start_time + "' AND " + date_filed + " <= '" + end_time + "'"
        one_day_result = summary.field_calculate(table, region_id_field, c_field_list, expression)
except Exception as err:
    print(err.args[0])
