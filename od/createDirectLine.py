# -*- coding: UTF-8 -*-
import sys
import arcpy
import math
reload(sys)
sys.setdefaultencoding('utf-8')

direction_num = 16  # 方向数
distance_name = "Distance"  # 平均距离字段名称（输入中为 distance_name_i 形式，输出结果中为distance_name）
volume_name = "Volume"  # 流量（人数）字段名称（输入中为 volume_name_i 形式，输出结果中为volume_name）
region_id_field = "QBM"  # 区域编码字段名称，也在输出结果中
region_name_field = "SSQ"  # 区域名称字段名称，也在输出结果中
direction_name = "Direction"  # 输出结果中存储方向的字段名称
bound_ds_area = "BOUND_17_H2W_DS_16"  # 包含有16方向线信息的区域要素

out_field_list = [[region_id_field, "TEXT"],
                  [region_name_field, "TEXT"],
                  [distance_name, "DOUBLE"],
                  [volume_name, "DOUBLE"],
                  [direction_name, "DOUBLE"]]  # 输出要素类属性集合

# arcpy.env.workspace = "C:/MData/WorkAndHome.gdb"
arcpy.env.workspace = "C:/MData/TestGDB.gdb"
try:
    arcpy.env.overwriteOutput = True

    # 创建方向线要素类模板
    template_out_name = "TEMP_LINE"  # 方向线模板名称
    geometry_type = "POLYLINE"  # 要素类型
    spatial_reference = arcpy.Describe(bound_ds_area).spatialReference  # 统一空间参考
    # 创建模板要素
    arcpy.CreateFeatureclass_management(arcpy.env.workspace, template_out_name, geometry_type,
                                        "", "DISABLED", "DISABLED", spatial_reference)
    for field in out_field_list:
        arcpy.AddField_management(template_out_name, field[0], field[1])
    # 获得每个区域中心点
    center_points = {}
    bp_cursor = arcpy.da.SearchCursor(bound_ds_area, ["SHAPE@TRUECENTROID", region_id_field])
    for row in bp_cursor:
        r_id = row[1]
        r_cp = row[0]
        r_center_point = arcpy.Point(r_cp[0], r_cp[1])
        center_points[r_id] = r_center_point

    bf_cursor = arcpy.SearchCursor(bound_ds_area)
    insert_field = []
    for filed in out_field_list:
        insert_field.append(filed[0])
    insert_field.append("SHAPE@")

    out_class = []
    for row in bf_cursor:
        r_filed = {}
        r_id = row.getValue(region_id_field)
        r_name = row.getValue(region_name_field)
        r_filed[region_id_field] = r_id
        r_filed[region_name_field] = r_name
        r_center_point = center_points[r_id]
        out_line_name = region_id_field + "_L_" + r_id
        arcpy.CreateFeatureclass_management(arcpy.env.workspace, out_line_name, geometry_type,
                                            template_out_name, "DISABLED", "DISABLED", spatial_reference)
        out_class.append(out_line_name)
        r_insert_cur = arcpy.da.InsertCursor(out_line_name, insert_field)
        polylines = []
        for i in range(1, direction_num + 1):
            r_distance = row.getValue(distance_name + "_" + str(i))
            r_volume = row.getValue(volume_name + "_" + str(i))
            r_filed[distance_name] = r_distance
            r_filed[volume_name] = r_volume
            r_filed[direction_name] = i
            r_cos = math.cos((i - 1) / 8.0 * math.pi)
            r_sin = math.sin((i - 1) / 8.0 * math.pi)
            r_dx = r_distance * r_cos
            r_dy = r_distance * r_sin
            r_nx = r_center_point.X + r_dx
            r_ny = r_center_point.Y + r_dy
            end_point = arcpy.Point(r_nx, r_ny)
            r_polyline = arcpy.Polyline(arcpy.Array([r_center_point, end_point]))

            insert_row_list = []
            for filed in insert_field:
                if filed == "SHAPE@":
                    insert_row_list.append(r_polyline)
                else:
                    insert_row_list.append(r_filed[filed])
            r_insert_cur.insertRow(insert_row_list)

except Exception as err:
    print(err.args[0])
