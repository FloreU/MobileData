# -*- coding: UTF-8 -*-
from od import cartoshp
import sys
import arcpy

reload(sys)
sys.setdefaultencoding('utf-8')


# 生成方向线参数
direction_num = 16  # 方向数
distance_name = "Distance"  # 平均距离字段名称（输入中为 distance_name_i 形式，输出结果中为distance_name）
volume_name = "Volume"  # 流量（人数）字段名称（输入中为 volume_name_i 形式，输出结果中为volume_name）
region_id_field = "QBM"  # 区域编码字段名称，也在输出结果中
region_name_field = "SSQ"  # 区域名称字段名称，也在输出结果中
direction_name = "Direction"  # 输出结果中存储方向的字段名称
bound_ds_area = "BOUND_17_H2W_DS"  # 包含有16方向线信息的区域要素

out_field_list = [[region_id_field, "TEXT"],
                  [region_name_field, "TEXT"],
                  [distance_name, "DOUBLE"],
                  [volume_name, "DOUBLE"],
                  [direction_name, "DOUBLE"]]  # 输出要素类属性集合
out_path = "C:/MData/WorkAndHome.gdb"

regionBoundaryFeature = "BOUND_17"  # 统计识别区域数据
regionIDFieldStr = "QBM"  # 区域代码字段
# 生成流向面参数
work2HomeTableSum = "W2H_Stats_SUM"  # 工作地到居住地流量汇总表格
home2WorkTableSum = "H2W_Stats_SUM"  # 居住地到工作地流量汇总表格
WORK_NUM = "WORK_NUM"  # WH、W2H表中表示工作人数字段
HOME_NUM = "HOME_NUM"  # WH、H2W表中表示居住人数字段
statsW2HNumField = "SUM_" + WORK_NUM  # work2HomeTableSum表格中表示工作人数字段
statsH2WNumField = "SUM_" + HOME_NUM  # home2WorkTableSum表格中表示居住人数字段
workRegionIDFieldStr = "WORK_ID_" + regionIDFieldStr  # 工作地区域代码字段
homeRegionIDFieldStr = "HOME_ID_" + regionIDFieldStr  # 居住地区域代码字段

arcpy.env.workspace = "C:/MData/WorkAndHome.gdb"

try:
    arcpy.env.overwriteOutput = True
    parameter_obj = cartoshp.init_parameter(bound_ds_area, region_id_field, region_name_field,
                                            distance_name, volume_name, direction_name, direction_num,
                                            out_path, out_field_list)
    # 创建方向线要素类模板
    line_template_obj = cartoshp.create_line_template(bound_ds_area, out_field_list)
    # 获得每个区域中心点
    center_points = cartoshp.get_center_point(bound_ds_area, region_id_field)
    # 创建方向线
    out_lines = cartoshp.create_all_direction_lines(center_points, line_template_obj, parameter_obj)
    # 创建流向面
    h2w_od_obj = cartoshp.stats_od_table(home2WorkTableSum, homeRegionIDFieldStr, workRegionIDFieldStr, statsH2WNumField)
    out_list = cartoshp.create_od_polygon(regionBoundaryFeature, h2w_od_obj, regionIDFieldStr, volume_name)
except Exception as err:
    print(err.args[0])
