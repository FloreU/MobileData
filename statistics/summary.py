import arcpy
import sys

from statistics import sys_arcpy

reload(sys)
sys.setdefaultencoding('utf-8')


def field_calculate(in_feature, id_field, field_list, expression):
    feature_field_list = sys_arcpy.get_all_fields(in_feature)
    real_field_list = []
    for field in field_list:
        if field in feature_field_list:
            real_field_list.append(field)
    field_list = real_field_list
    cursor = arcpy.SearchCursor(in_feature, expression)
    result_obj = {}
    for row in cursor:
        region_id = row.getValue(id_field)
        if region_id not in result_obj:
            tmp_obj = {}
            for field in field_list:
                tmp_obj[field] = {"Sum": 0, "Count": 0}
            result_obj[region_id] = tmp_obj
        region_obj = result_obj[region_id]
        for field in field_list:
            field_value = row.getValue(field)
            region_obj[field]["Sum"] += field_value
            region_obj[field]["Count"] += 1
        result_obj[region_id] = region_obj
    del cursor, row
    for obj_key in result_obj:
        for key in result_obj[obj_key]:
            result_obj[obj_key][key]["Average"] = (
                result_obj[obj_key][key]["Sum"] / result_obj[obj_key][key]["Count"]
            )

    return result_obj


def calculate_average(result_obj,num):
    for obj_key in result_obj:
        for key in result_obj[obj_key]:
            result_obj[obj_key][key]["RealAverage"] = (
                result_obj[obj_key][key]["Sum"] / num
            )

    return result_obj


def save_table(out_table,result_obj):

    return

