# -*- coding: UTF-8 -*-
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

arcpy.env.workspace = "C:/MData/WorkAndHome.gdb"
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
    var_access.save_json(table_name_list, "DayTableSex.txt")
    var_access.save_var(table_name_list, "DayTableSex.pkl")

except Exception as err:
    print(err.args[0])
