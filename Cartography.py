# -*- coding: UTF-8 -*-
import os
from arcgisHelper import FeatureCartography
import arcgisHelper as ah


def main():
    # fc = FeatureCartography("C:/Workspace/arcpy_mdb_test.mdb", "C:/Workspace/wuhan_style.mxd",
    #                         "C:/Workspace/empty.mxd", ["w1", "w2"])
    # fc.main_process(["wuhan", "www"], "wuhan_fc")

    # 制图模板初始化，gdb、style.mxd、empty.mxd、style中的两个模板图层的名字
    ah.set_env("C:/MData/WorkAndHome.gdb")
    fc = FeatureCartography("C:/MData/WorkAndHome.gdb", "C:/MData/style.mxd",
                            "C:/MData/empty.mxd", ["TemplateA", "TemplateL"],
                            {"TemplateA": "Volume", "TemplateL": "Volume"})
    # 对输入的两个要素使用上述模板进行渲染，要素输入的顺序和渲染模板相对应
    qbm_list = [str(n) for n in xrange(420102, 420108)] + [str(n) for n in xrange(420111, 420122)]
    for qbm in qbm_list:
        feature_a = "QBM_A_" + qbm
        feature_l = "QBM_L_" + qbm
        feature_out_name = "wuhan_h2w_od_" + qbm
        fc.main_process([feature_a, feature_l], feature_out_name)


    # fc.create_mxd_from_feature([("QBM_A_420102", "TemplateA"), ("QBM_L_420102", "TemplateL")], "C:/MData/wuhan_fc_fc.mxd")

if __name__ == '__main__':
    main()
