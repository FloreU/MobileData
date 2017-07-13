# -*- coding: UTF-8 -*-
# 将性别总表分割成性别预分割表
import arcpy
import sys
from statistics import separate

reload(sys)
sys.setdefaultencoding('utf-8')
table_name = "GRID_SEX"
pre_table_name = [table_name + "_0_10",
                  table_name + "_11_20",
                  table_name + "_21_30"]
time_range_list = [["2016-06-01", "2016-06-11"],
                   ["2016-06-11", "2016-06-21"],
                   ["2016-06-21", "2016-06-31"]]
date_filed = "TIME_DUR"

arcpy.env.workspace = "E:/InformationCenter/Time_Sex.gdb"
print("前期导入 -- 100%")
try:
    arcpy.env.overwriteOutput = True
    for i in range(len(pre_table_name)):
        separate.separate_table_days_range(table_name, pre_table_name[i], date_filed, time_range_list[i])

except Exception as err:
    print(err.args[0])
