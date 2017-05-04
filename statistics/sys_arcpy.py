# -*- coding: UTF-8 -*-
import arcpy
import math
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def get_all_fields(in_feature, attribute="name"):
    fields = arcpy.ListFields(in_feature)
    field_list = []
    for field in fields:
        value = field.name
        field_list.append(value)
    return field_list
