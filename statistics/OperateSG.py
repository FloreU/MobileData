# -*- coding: UTF-8 -*-
import arcpy
import sys
from statistics import statsGrid
reload(sys)
sys.setdefaultencoding('utf-8')


print("前期导入 -- 100%")
try:
    arcpy.env.workspace = "C:/TestOSG.gdb"
    arcpy.env.overwriteOutput = True

    # 要素转点
    print("格网转点...")
    mobileGridFeature = "wuhan_grid"
    mobilePointFeature = mobileGridFeature + "2Point"
    arcpy.FeatureToPoint_management(mobileGridFeature, mobilePointFeature, "CENTROID")
    print("格网转点 -- 100%")
    # 识别区域
    print("点区域识别...")
    regionBoundaryFeature = "wuhanRegion_84"
    identifyPointFeatures = mobilePointFeature + "IdBound"
    arcpy.Identity_analysis(mobilePointFeature, regionBoundaryFeature, identifyPointFeatures)
    print("点区域识别 -- 100%")
    # 连接统计表格与识别区域后要素图层
    print("统计数据连接要素...")
    statisticsTable = "FM"
    statisticsTableJoinField = "GRID_ID"
    identifyPointJoinField = "grid_id"
    idJoinFields = ["XZQDM", "XZQMC"]
    arcpy.JoinField_management(statisticsTable, statisticsTableJoinField,
                               identifyPointFeatures, identifyPointJoinField, idJoinFields)
    print("统计数据连接要素 -- 100%")
    # 分拆表格
    separateField = "TIME_DUR"
    separateTableList = statsGrid.separateTableByFieldValue(statisticsTable, separateField)
    print("分拆表格 -- 100%")
    # 汇总每个时间点每个区域的总数
    sFieldsList = ["NUM_MALE", "NUM_FEMALE", "NUM_OTHER", "NUM_ALL",
                   "AGE_15_19", "AGE_20_24", "AGE_25_29", "AGE_30_34",
                   "AGE_35_39", "AGE_40_44", "AGE_44_49", "AGE_49_91", "AGE_OTHER"]
    sType = "SUM"
    regionIDField = "XZQMC;TIME_DUR"
    summaryTableNameList = statsGrid.summaryAllStatisticsTable(separateTableList, sFieldsList, sType, regionIDField)

    # 复制区域边界（汇总统计结果）
    statisticsRegionFeatures = regionBoundaryFeature + "_SUM"
    arcpy.CopyFeatures_management(regionBoundaryFeature, statisticsRegionFeatures)

    # 添加字段：居住人口、总工作人口、区内工作人口、外出工作人口、外来工作人口
    # 居住人口 >= 总工作人口 = 区内工作人口 + 外出工作人口
    # 外来工作人口单独算
    arcpy.AddField_management(statisticsRegionFeatures, "ResidentP", "LONG")
    arcpy.AddField_management(statisticsRegionFeatures, "WorkingP", "LONG")
    arcpy.AddField_management(statisticsRegionFeatures, "InsideWP", "LONG")
    arcpy.AddField_management(statisticsRegionFeatures, "OutsideWP", "LONG")
    arcpy.AddField_management(statisticsRegionFeatures, "ExternalWP", "LONG")
except Exception as err:
    print(err.args[0])
