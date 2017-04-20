# -*- coding: UTF-8 -*-
import sys
import arcpy
import math

reload(sys)
sys.setdefaultencoding('utf-8')

regionBoundaryFeature = "BOUND_17"  # 统计识别区域数据
regionIDFieldStr = "QBM"  # 区域代码字段

work2HomeTableSum = "W2H_Stats_SUM"  # 工作地到居住地流量汇总表格
home2WorkTableSum = "H2W_Stats_SUM"  # 居住地到工作地流量汇总表格
WORK_NUM = "WORK_NUM"  # WH、W2H表中表示工作人数字段
HOME_NUM = "HOME_NUM"  # WH、H2W表中表示居住人数字段
statsW2HNumField = "SUM_" + WORK_NUM  # work2HomeTableSum表格中表示工作人数字段
statsH2WNumField = "SUM_" + HOME_NUM  # home2WorkTableSum表格中表示居住人数字段
workRegionIDFieldStr = "WORK_ID_" + regionIDFieldStr  # 工作地区域代码字段
homeRegionIDFieldStr = "HOME_ID_" + regionIDFieldStr  # 居住地区域代码字段

volume_name = "Volume"
arcpy.env.workspace = "C:/MData/WorkAndHome.gdb"


def statsOD(od_table, origin_field, destination_field, num_field):
    od_obj = {}
    od_table_cur = arcpy.SearchCursor(od_table)
    for row in od_table_cur:
        origin_id = row.getValue(origin_field)
        destination_id = row.getValue(destination_field)
        volume = row.getValue(num_field)
        if origin_id == '':
            origin_id = "otherR"
        if destination_id == '':
            destination_id = "otherR"
        if origin_id in od_obj:
            od_obj[origin_id][destination_id] = volume
        else:
            od_obj[origin_id] = {}
            od_obj[origin_id][destination_id] = volume
    del od_table_cur
    return od_obj


def createODPolygon(region_feature, od_obj, region_id_field, volume_field):
    region_cur = arcpy.SearchCursor(region_feature)
    out_od_list = []
    for row in region_cur:
        origin_id = row.getValue(region_id_field)
        if origin_id == '':
            origin_id = "otherR"
        out_od = region_id_field + "_A_" + origin_id
        out_od_list.append(out_od)
        arcpy.CopyFeatures_management(region_feature, out_od)
        arcpy.AddField_management(out_od, volume_field, "LONG")
        out_od_cur = arcpy.UpdateCursor(out_od)
        for out_cur_row in out_od_cur:
            destination_id = out_cur_row.getValue(region_id_field)
            if destination_id == '':
                destination_id = "otherR"
            volume = od_obj[origin_id][destination_id]
            out_cur_row.setValue(volume_field, volume)
            out_od_cur.updateRow(out_cur_row)
        del out_od_cur
    del region_cur
    return out_od_list


try:
    arcpy.env.overwriteOutput = True
    h2w_od_obj = statsOD(home2WorkTableSum, homeRegionIDFieldStr, workRegionIDFieldStr, statsH2WNumField)
    out_list = createODPolygon(regionBoundaryFeature, h2w_od_obj, regionIDFieldStr, volume_name)
except Exception as err:
    print(err.args[0])
