# -*- coding: UTF-8 -*-
import sys
import arcpy
import math

reload(sys)
sys.setdefaultencoding('utf-8')


def init_parameter(bound, id_field, name_field,
                   distance_name, volume_name, direction_name, direction_num,
                   out_path, out_field_list):
    parameter_obj = {"bound": bound, "id_field": id_field, "name_field": name_field,
                     "distance_name": distance_name, "volume_name": volume_name,
                     "direction_name": direction_name, "direction_num": direction_num,
                     "out_path": out_path, "out_field_list": out_field_list}
    return parameter_obj


# # 方向线
def create_line_template(bound, out_field_list):
    # 创建方向线要素类模板
    # bound：边界区域要素
    # out_field_list：输出方向线要素包含属性字段

    line_template_name = "OD_TEMP_LINE"  # 方向线模板名称
    geometry_type = "POLYLINE"  # 要素类型
    spatial_reference = arcpy.Describe(bound).spatialReference  # 统一空间参考
    # 创建模板要素
    arcpy.CreateFeatureclass_management(arcpy.env.workspace, line_template_name, geometry_type,
                                        "", "DISABLED", "DISABLED", spatial_reference)
    for field in out_field_list:
        arcpy.AddField_management(line_template_name, field[0], field[1])
    line_template_obj = {"name": line_template_name, "type": geometry_type, "spatial_ref": spatial_reference}
    return line_template_obj


def get_center_point(bound, id_field):
    # 获得每个区域中心点
    # bound：边界区域要素
    # id_field：边界区域中表示id区域编码的字段
    center_points = {}
    bound_da_cursor = arcpy.da.SearchCursor(bound, ["SHAPE@TRUECENTROID", id_field])
    for row in bound_da_cursor:
        bound_id = row[1]
        center_point_xy = row[0]
        center_point = arcpy.Point(center_point_xy[0], center_point_xy[1])
        center_points[bound_id] = center_point
    return center_points


def create_single_direction_line(insert_cur, center_point, filed_obj, insert_field, distance_name, direction_name):
    # 插入一条方向线
    # insert_cur：插入记录游标（注意游标生成按insert_field生成）
    # center_point：中心点坐标（起点坐标）
    # filed_obj：属性对象
    # insert_field：插入要素类中对应的属性列表（顺序也对应）
    # distance_name：filed_obj中表示距离的属性（和插入表中的距离字段名称一致）
    # direction_name：filed_obj中表示方向标识的属性（和插入表中的方向字段名称一致）

    direction_num = filed_obj["direction_num"]
    distance = filed_obj[distance_name]
    end_point = calculate_end_point(center_point, distance, filed_obj[direction_name], direction_num)
    od_polyline = arcpy.Polyline(arcpy.Array([center_point, end_point]))

    insert_row_list = []
    for filed in insert_field:
        if filed == "SHAPE@":
            insert_row_list.append(od_polyline)
        else:
            insert_row_list.append(filed_obj[filed])
    insert_cur.insertRow(insert_row_list)
    return


def calculate_end_point(center_point, distance, direction_sign, direction_num):
    # 返回终点端点对象
    # center_poin：中心点坐标，arcp.Point对象
    # distance：距离长度
    # direction_sign：方向标识，正整数，从1开始，表示X轴正方向
    # direction_num：分为几个方向，8、16、32等
    theta_cos = math.cos((direction_sign - 1) / direction_num * 2 * math.pi)
    theta_sin = math.sin((direction_sign - 1) / direction_num * 2 * math.pi)
    e_dx = distance * theta_cos
    e_dy = distance * theta_sin
    e_x = center_point.X + e_dx
    e_y = center_point.Y + e_dy
    end_point = arcpy.Point(e_x, e_y)
    return end_point


def create_region_direction_lines(bound_cursor_row, center_points, line_template_obj, parameter_obj, insert_field):
    id_field = parameter_obj["id_field"]
    name_filed = parameter_obj["name_filed"]
    distance_name = parameter_obj["distance_name"]
    volume_name = parameter_obj["volume_name"]
    direction_name = parameter_obj["direction_name"]
    direction_num = parameter_obj["direction_num"]
    out_path = parameter_obj["out_path"]
    filed_obj = {}
    bound_id = bound_cursor_row.getValue(id_field)
    bound_name = bound_cursor_row.getValue(name_filed)
    filed_obj[id_field] = bound_id
    filed_obj[name_filed] = bound_name
    center_point = center_points[bound_id]
    out_name = id_field + "_L_" + bound_id
    arcpy.CreateFeatureclass_management(out_path, out_name,
                                        line_template_obj["type"], line_template_obj["name"],
                                        "DISABLED", "DISABLED",
                                        line_template_obj["spatial_ref"])
    insert_cur = arcpy.da.InsertCursor(out_name, insert_field)
    for i in range(1, direction_num + 1):
        distance = bound_cursor_row.getValue(distance_name + "_" + str(i))
        volume = bound_cursor_row.getValue(volume_name + "_" + str(i))
        filed_obj[distance_name] = distance
        filed_obj[volume_name] = volume
        filed_obj[direction_name] = i
        create_single_direction_line(insert_cur, center_point, filed_obj, insert_field, distance_name, direction_name)
    return out_name


def create_all_direction_lines(center_points, line_template_obj, parameter_obj):
    bound_cursor = arcpy.SearchCursor(parameter_obj["bound"])
    insert_field = []
    for filed in parameter_obj["out_field_list"]:
        insert_field.append(filed[0])
    insert_field.append("SHAPE@")
    out_direction_lines = []
    for row in bound_cursor:
        out_name = create_region_direction_lines(row, center_points, line_template_obj, parameter_obj, insert_field)
        out_direction_lines.append(out_name)
    return out_direction_lines


# # 流向面
def stats_od_table(od_table, origin_field, destination_field, num_field):
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


def create_od_polygon(region_feature, od_obj, region_id_field, volume_field):
    region_cur = arcpy.SearchCursor(region_feature)
    out_od_polygons = []
    for row in region_cur:
        origin_id = row.getValue(region_id_field)
        if origin_id == '':
            origin_id = "otherR"
        out_od = region_id_field + "_A_" + origin_id
        out_od_polygons.append(out_od)
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
    return out_od_polygons
