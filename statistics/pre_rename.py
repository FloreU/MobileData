import arcpy
import sys
from statistics import var_access

reload(sys)
sys.setdefaultencoding('utf-8')
var_file_pkl1 = "DayTableAge.pkl"
var_file_json1 = "DayTableAge.txt"
var_file_pkl2 = "DayTableSex.pkl"
var_file_json2 = "DayTableSex.txt"

delete_str = ["0_10_", "11_20_", "21_30_"]

arcpy.env.workspace = "E:/InformationCenter/Time_Age.gdb"


def pre_rename(var_file, del_str):
    table_name_list = var_access.load_var(var_file)
    re_table_name_list = []
    for table_name in table_name_list:
        flag = False
        re_table_name = None
        for d_str in del_str:
            if d_str in table_name:
                re_table_name = table_name.replace(d_str, "")
                arcpy.Rename_management(table_name, re_table_name)
                flag = True
                break
        if flag:
            re_table_name_list.append(re_table_name)
        else:
            re_table_name_list.append(table_name)
    var_access.save_var(re_table_name_list, var_file)
    return re_table_name_list


try:
    arcpy.env.overwriteOutput = True
    re_name_list1 = pre_rename(var_file_pkl1, delete_str)
    var_access.save_json(re_name_list1, var_file_json1)
    # re_name_list2 = pre_rename(var_file_pkl2, delete_str)
    # var_access.save_json(re_name_list2, var_file_json2)
except Exception as err:
    print(err.args[0])
