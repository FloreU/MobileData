# -*- coding: UTF-8 -*-
import arcpy
import os
from arcpy import mapping


class FeatureCartography:
    def __init__(self, env_path, style_mxd_path, void_mxd_path, style_lyr_list):
        self.env_path = env_path
        arcpy.env.workspace = env_path
        self.void_mxd_path = void_mxd_path
        self.style_mxd_path = style_mxd_path
        self.style_lyr_list = style_lyr_list

    # 将gdb、mdb工作空间中的要素类转化成图层对象，并存储在一个mxd中
    def create_mxd_from_feature(self, feature_tuple_list, out_mxd):
        mxd = arcpy.mapping.MapDocument(self.void_mxd_path)
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        for feature, lyr_name in feature_tuple_list:
            new_lyr_name = feature + "_" + lyr_name
            arcpy.MakeFeatureLayer_management(feature, new_lyr_name)
            lyr = arcpy.mapping.Layer(new_lyr_name)
            arcpy.mapping.AddLayer(df, lyr, "AUTO_ARRANGE")
        mxd.saveACopy(out_mxd)
        return out_mxd

    # 使用渲染图层对源图层进行渲染
    def mxd_render(self, source_mxd_path):
        source_mxd = arcpy.mapping.MapDocument(source_mxd_path)
        style_mxd = arcpy.mapping.MapDocument(self.style_mxd_path)
        source_df = arcpy.mapping.ListDataFrames(source_mxd)[0]
        style_df = arcpy.mapping.ListDataFrames(style_mxd)[0]
        for source_lyr in source_df:
            source_lyr_name = source_lyr.name
            style_lyr_name = source_lyr_name.split("_")[-1]
            style_lyr = arcpy.mapping.ListLayers(style_mxd, style_lyr_name, style_df)[0]
            arcpy.mapping.UpdateLayer(source_df, source_lyr, style_lyr, True)
            # arcpy.mapping.UpdateLayer(style_df, style_lyr, source_lyr, False)
        source_mxd.save()
        # style_mxd.save()
        del source_mxd
        del style_mxd

    def main_process(self, feature_list, out_name):
        if len(feature_list) != len(self.style_lyr_list):
            return
        out_mxd_name = os.path.dirname(self.env_path) + "/" + out_name + ".mxd"
        self.mxd_render(self.create_mxd_from_feature(zip(feature_list, self.style_lyr_list), out_mxd_name))


def main():
    # fc = FeatureCartography("C:/Workspace/arcpy_mdb_test.mdb", "C:/Workspace/wuhan_style.mxd",
    #                         "C:/Workspace/empty.mxd", ["w1", "w2"])
    # fc.main_process(["wuhan", "www"], "wuhan_fc")

    # 制图模板初始化，gdb、style.mxd、empty.mxd、style中的两个模板图层的名字
    fc = FeatureCartography("C:/MData/WorkAndHome.gdb", "C:/MData/Style.mxd",
                            "C:/MData/Empty.mxd", ["TemplateA", "TemplateL"])
    # 对输入的两个要素使用上述模板进行渲染，要素输入的顺序和渲染模板相对应
    fc.main_process(["QBM_A_420102", "QBM_L_420102"], "wuhan_fc")
    # fc.create_mxd_from_feature([("QBM_A_420102", "TemplateA"), ("QBM_L_420102", "TemplateL")], "C:/MData/wuhan_fc_fc.mxd")

if __name__ == '__main__':
    main()

