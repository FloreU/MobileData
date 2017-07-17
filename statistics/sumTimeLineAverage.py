# -*- coding: UTF-8 -*-
# 生成各个属性工作日、均值均值时间线
import arcpy
import sys
import time
from statistics import var_access
from statistics import timeline

reload(sys)
sys.setdefaultencoding('utf-8')

# 统一属性
tmp_var_dir = "E:/InformationCenter/MobileData/tmp_var/"
date_filed = "TIME_DUR"
region_id_field = "GRID_ID"
template_table = "TIME_LINE_TEMPLATE"
change_template_table="CHANGE_TIME_LINE_TEMPLATE"
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


try:
    arcpy.env.workspace = c_gdb
    arcpy.env.overwriteOutput = True
    work_day_table = timeline.create_name_list("D_GRID", curr_type, year_month, work_day)
    rest_day_table = timeline.create_name_list("D_GRID", curr_type, year_month, rest_day)
    work_rest_day_table = {"WORK": work_day_table, "REST": rest_day_table}  # 工作日休息日对应表格
    all_result = timeline.sum_every_time(work_rest_day_table, c_field_list, region_id_field, date_filed)
    var_access.save_var(all_result, (tmp_var_dir + curr_type + "_time_line.pkl"))

    timeline.create_time_line_table(c_sum_gdb, template_table, region_id_field)

    arcpy.env.workspace = c_sum_gdb
    arcpy.env.overwriteOutput = True

    all_result = var_access.load_var((tmp_var_dir + curr_type + "_time_line.pkl"))
    result_table_list = timeline.insert_time_line_table(all_result, work_rest_day_table, c_field_list,
                                                        c_sum_gdb, template_table, region_id_field)

    timeline.create_change_time_line_table(c_sum_gdb, change_template_table, region_id_field)
    timeline.insert_slope_time_line_table(all_result, work_rest_day_table, c_field_list,
                                          c_sum_gdb, change_template_table, region_id_field)
    timeline.insert_rate_time_line_table(all_result, work_rest_day_table, c_field_list,
                                         c_sum_gdb, change_template_table, region_id_field)

except Exception as err:
    print(err.args[0])
