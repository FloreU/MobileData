# -*- coding: UTF-8 -*-
import arcpy
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def get_all_fields(in_feature):
    fields = arcpy.ListFields(in_feature)
    field_list = []
    for field in fields:
        value = field.name
        field_list.append(value)
    return field_list


def run_time(fcn):
    time1 = time.time()
    fcn()
    time2 = time.time()
    r_time = (time2 - time1) / 60
    print(r_time)
    return r_time
