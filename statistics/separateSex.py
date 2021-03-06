# -*- coding: UTF-8 -*-
# 将预分割的性别表分割成每日的性别时刻表
import arcpy
import sys
from statistics import time_list
from statistics import separate
from statistics import var_access

reload(sys)
sys.setdefaultencoding('utf-8')

start_day1 = "2016-06-01"
end_day1 = "2016-06-10"
table_name1 = "GRID_SEX_0_10"
start_day2 = "2016-06-11"
end_day2 = "2016-06-20"
table_name2 = "GRID_SEX_11_20"
start_day3 = "2016-06-21"
end_day3 = "2016-06-30"
table_name3 = "GRID_SEX_21_30"

date_filed = "TIME_DUR"

var_file_pkl1 = "DayTableAge.pkl"
var_file_json1 = "DayTableAge.txt"
var_file_pkl2 = "DayTableSex.pkl"
var_file_json2 = "DayTableSex.txt"
tmp_var_dir = "E:/InformationCenter/MobileData/tmp_var"

arcpy.env.workspace = "E:/InformationCenter/Time_Sex.gdb"
print("前期导入 -- 100%")
try:
    arcpy.env.overwriteOutput = True
    day_list1 = time_list.create_days_range(start_day1, end_day1)
    table_name_list1 = separate.separate_table_days(table_name1, date_filed, day_list1)
    day_list2 = time_list.create_days_range(start_day2, end_day2)
    table_name_list2 = separate.separate_table_days(table_name2, date_filed, day_list2)
    day_list3 = time_list.create_days_range(start_day3, end_day3)
    table_name_list3 = separate.separate_table_days(table_name3, date_filed, day_list3)
    table_name_list = table_name_list1 + table_name_list2 + table_name_list3
    var_access.save_json(table_name_list, (tmp_var_dir + "/" + var_file_json2))
    var_access.save_var(table_name_list, (tmp_var_dir + "/" + var_file_pkl2))

except Exception as err:
    print(err.args[0])
