# -*- coding: UTF-8 -*-
import arcpy
from arcpy import mapping
import os
import math
from jenks import jenks

current_env_path = ""
region_dict = {
    "420102": "江岸区",
    "420103": "江汉区",
    "420104": "硚口区",
    "420105": "汉阳区",
    "420106": "武昌区",
    "420107": "青山区",
    "420111": "洪山区",
    "420112": "东西湖区",
    "420113": "汉南区",
    "420114": "蔡甸区",
    "420115": "江夏区",
    "420116": "黄陂区",
    "420117": "新洲区",
    "420118": "武汉开发区",
    "420119": "东湖开发区",
    "420120": "东湖风景区",
    "420121": "化工区"
}


# 根据路径及名字获取游标
def get_rows(name):
    print "get search cursor:", name
    return arcpy.SearchCursor(name)


# 获取可用于更新的游标
def get_update_rows(name):
    print "get update cursor:", name
    return arcpy.UpdateCursor(name)


# 给某一行对象添加一属性值
def add_field_value(value, field_name, row, cursor):
    row.setValue(field_name, value)
    cursor.updateRow(row)


# ·TEXT —名称或其他文本特性。
# ·FLOAT —特定范围内含小数值的数值。
# ·DOUBLE —特定范围内含小数值的数值。
# ·SHORT —特定范围内不含小数值的数值；编码值。
# ·LONG —特定范围内不含小数值的数值。
# ·DATE —日期和/或时间。
# ·BLOB —影像或其他多媒体。
# ·RASTER —栅格影像。
# ·GUID —GUID 值
def add_field(field_name, field_type, table_name):
    if field_name in arcpy.ListFields(table_name):
        arcpy.DeleteField_management(table_name, field_name)
    arcpy.AddField_management(table_name, field_name, field_type)
    print "add:", field_type, " type field", field_name, "to table", table_name


def set_env(env_path, overwrite=True):
    print "set env:", env_path
    arcpy.env.workspace = env_path
    arcpy.env.overwriteOutput = overwrite
    global current_env_path
    current_env_path = env_path


def copy_feature(feature_name, env_path, describe):
    arcpy.FeatureClassToFeatureClass_conversion(feature_name, env_path, feature_name + describe)
    print "copy done", feature_name + describe
    return feature_name + describe


# 根据表格名字获取指定字段为主码的dict
def create_summary_dict(table_name, summary_field):
    rows = get_rows(table_name)
    summary_dict = {}
    for row in rows:
        summary_id = row.getValue(summary_field)
        summary_dict[summary_id] = {}
    return summary_dict


# 自然断点法
def field_jenks(in_table, field_name, class_num):
    rows = get_rows(in_table)
    data_list = [row.getValue(field_name) for row in rows]
    result_data_list = jenks(data_list, class_num)
    print result_data_list
    return [float(group[-1]) for group in result_data_list]


# 图层合并
def field_append(source, target, geometry_type):
    arcpy.CreateFeatureclass_management(current_env_path, target, geometry_type, source[0])
    arcpy.Append_management(source, target)


# 字段计算方法
# 工作空间中的表格名字 table_name
# 处理函数的列表 functions
# 处理结果字段名字的列表 result_fields
# 辅助的变量 aux
def calculate_fields(table_name, functions, result_fields, field_type="DOUBLE"):
    # 定义一个对rows迭代运用函数的迭代方法
    def calculator_rows(rows, function, result_field_name):
        for row in rows:
            result = function(row)
            add_field_value(result, result_field_name, row, rows)
    # table_rows = get_update_rows(t_name)
    for f, r in zip(functions, result_fields):
        print "on processing ", f.__name__
        # table_rows.reset()
        add_field(r, field_type, table_name)
        table_rows = get_update_rows(table_name)
        calculator_rows(table_rows, f, r)
        del table_rows


# 字段汇总类
class SummaryGrid(object):
    def __init__(self, in_table, out_table, summary_dict, in_summary_field, out_summary_field, describe, data_type="DOUBLE"):
        self.in_table = in_table
        self.out_table = out_table
        self.summary_dict = summary_dict
        self.in_summary_field = in_summary_field
        self.out_summary_field = out_summary_field
        self.describe = describe
        self.data_type = data_type

    def update(self, new_fields):
        new_copy_table = copy_feature(self.out_table, current_env_path, self.describe)
        for new_field in new_fields:
            add_field(new_field, self.data_type, new_copy_table)
        point_edit_rows = get_update_rows(new_copy_table)
        for pe_row in point_edit_rows:
            pe_id = pe_row.getValue(self.out_summary_field)
            pe_obj = self.summary_dict[pe_id]
            for new_field in new_fields:
                # if pe_obj[new_field] != 0:
                add_field_value(pe_obj[new_field], new_field, pe_row, point_edit_rows)
        del point_edit_rows

    # summary_field 需要汇总的字段；
    # data_fields 数据字段；
    # new_field 汇总结果新建字段
    def summary(self, data_fields, new_fields, summary_function, *end_process_func):
        def init_pid_dict(init_value):
            for v in self.summary_dict.itervalues():
                for new_field in new_fields:
                    v[new_field] = init_value
        init_pid_dict(0.0)
        rows = get_rows(self.in_table)
        for row in rows:
            s_id = row.getValue(self.in_summary_field)
            if s_id:
                data = [row.getValue(d_f) for d_f in data_fields]
                summary_function(self.summary_dict[s_id], new_fields, data)
        if end_process_func:
            end_process_func[0](self.summary_dict)
        self.update(new_fields)


# 要素制图类
# 调用示例
#     制图模板初始化，gdb、style.mxd、empty.mxd、style中的两个模板图层的名字
# fc = FeatureCartography("C:/MData/WorkAndHome.gdb", "C:/MData/wuhan_style.mxd",
#                           ["TemplateA", "TemplateL"], {"TemplateA": "Volume", "TemplateL": "volume"})
#     对输入的两个要素使用上述模板进行渲染，要素输入的顺序和渲染模板相对应
#     fc.main_process(["QBM_A_420102", "QBM_L_420102"], "wuhan_fc")

class FeatureCartography:
    def __init__(self, env_path, style_mxd_path, style_lyr_list, value_field_dict):
        self.env_path = env_path
        arcpy.env.workspace = env_path
        self.style_mxd_path = style_mxd_path
        self.style_lyr_list = style_lyr_list
        self.out_file_path = ""
        self.style_feature_dict = {}
        self.void_mxd_path = ""
        self.value_field_dict = value_field_dict

    # 将gdb、mdb工作空间中的要素类转化成图层对象，并存储在一个mxd中
    def create_mxd_from_feature(self):
        mxd = arcpy.mapping.MapDocument(self.void_mxd_path)
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        for lyr_name, feature in self.style_feature_dict.items():
            new_lyr_name = feature + "_" + lyr_name
            arcpy.MakeFeatureLayer_management(feature, new_lyr_name)
            lyr = arcpy.mapping.Layer(new_lyr_name)
            arcpy.mapping.AddLayer(df, lyr, "AUTO_ARRANGE")
        return mxd

    def replace_style_data_source(self, new_title):
        style_mxd = arcpy.mapping.MapDocument(self.style_mxd_path)
        style_df = arcpy.mapping.ListDataFrames(style_mxd)[0]
        for style_lyr in style_df:
            style_lyr_name = style_lyr.name
            feature_name = self.style_feature_dict[style_lyr_name]
            self.replace_data_source(style_lyr, self.env_path, feature_name)
            style_lyr.symbology.valueField = self.value_field_dict[style_lyr_name]
        self.set_document_title(style_mxd, new_title)
        arcpy.mapping.ExportToJPEG(style_mxd, self.out_file_path + ".jpg", "PAGE_LAYOUT",
                                   df_export_width=4962, df_export_height=7019, resolution=600)
        style_mxd.saveACopy(self.out_file_path + ".mxd")
        del style_mxd

    # 使用渲染图层对源图层进行渲染
    def mxd_render(self, source_mxd):
        # source_mxd = arcpy.mapping.MapDocument(source_mxd_path)
        style_mxd = arcpy.mapping.MapDocument(self.style_mxd_path)
        source_df = arcpy.mapping.ListDataFrames(source_mxd)[0]
        style_df = arcpy.mapping.ListDataFrames(style_mxd)[0]
        for style_lyr in style_df:
            style_lyr_name = style_lyr.name
            source_lyr_name = self.style_feature_dict[style_lyr_name] + "_" + style_lyr_name
            style_lyr = arcpy.mapping.ListLayers(style_mxd, style_lyr_name, style_df)[0]
            source_lyr = arcpy.mapping.ListLayers(source_mxd, source_lyr_name, source_df)[0]
            arcpy.mapping.UpdateLayer(style_df, style_lyr, source_lyr, True)
            # style_lyr.symbology.valueField = self.value_field_dict[style_lyr_name]
            # arcpy.mapping.UpdateLayer(style_df, style_lyr, source_lyr, False)
        # self.set_document_title(style_mxd, )
        arcpy.mapping.ExportToJPEG(style_mxd, self.out_file_path + ".jpg", "PAGE_LAYOUT",
                                   df_export_width=4962, df_export_height=7019, resolution=600)
        style_mxd.saveACopy(self.out_file_path + ".mxd")
        del source_mxd
        del style_mxd
        # for source_lyr in source_df:
        #     source_lyr_name = source_lyr.name
        #     style_lyr_name = source_lyr_name.split("_")[-1]
        #     style_lyr = arcpy.mapping.ListLayers(style_mxd, style_lyr_name, style_df)[0]
        #     arcpy.mapping.UpdateLayer(source_df, source_lyr, style_lyr, True)
        #     source_lyr.symbology.valueField = self.value_field_dict[style_lyr_name]
        #     # arcpy.mapping.UpdateLayer(style_df, style_lyr, source_lyr, False)
        # source_mxd.save()
        # arcpy.mapping.ExportToJPEG(source_mxd, self.out_file_path + ".jpg", "PAGE_LAYOUT",
        #                            df_export_width=4962, df_export_height=7019, resolution=600)
        # del source_mxd
        # del style_mxd

    def main_process(self, feature_list, out_name, title):
        assert len(feature_list) == len(self.style_lyr_list)
        self.out_file_path = os.path.dirname(self.env_path) + "/" + out_name
        self.style_feature_dict = {s: f for s, f in zip(self.style_lyr_list, feature_list)}
        # self.mxd_render(self.create_mxd_from_feature())
        self.replace_style_data_source(title)

    def set_document_title(self, mxd, title):
        mxd.title = title

    # ACCESS_WORKSPACE — A personal geodatabase or Access workspace
    # ARCINFO_WORKSPACE — An ArcInfo coverage workspace
    # CAD_WORKSPACE —A CAD file workspace
    # EXCEL_WORKSPACE —An Excel file workspace
    # FILEGDB_WORKSPACE —A file geodatabase workspace
    # NONE —Used to skip the parameter
    # OLEDB_WORKSPACE —An OLE database workspace
    # PCCOVERAGE_WORKSPACE —A PC ARC/INFO Coverage workspace
    # RASTER_WORKSPACE —A raster workspace
    # SDE_WORKSPACE —An SDE geodatabase workspace
    # SHAPEFILE_WORKSPACE —A shapefile workspace
    # TEXT_WORKSPACE —A text file workspace
    # TIN_WORKSPACE —A TIN workspace
    # VPF_WORKSPACE —A VPF workspace
    def replace_data_source(self, update_layer, source_workspace_path, source_feature_name,
                            source_workspace_type="FILEGDB_WORKSPACE"):
        update_layer.replaceDataSource(source_workspace_path, source_workspace_type, source_feature_name)
