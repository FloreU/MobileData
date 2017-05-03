# -*- coding: UTF-8 -*-
import arcpy
import sys
from statistics import statsGrid

reload(sys)
sys.setdefaultencoding('utf-8')


# - 数据
# -- 区域空间数据
mobileGridFeature = "wh_grid_250_54"  # 手机划分的格网数据
identifyPointJoinField = "grid_id"  # 手机格网数据中的格网id字段，也是用来连接字段时识区域后点数据的id字段
regionBoundaryFeature = "BOUND_17"  # 统计识别区域数据
regionIDFieldStr = "QBM"  # 区域代码字段
# -- 手机结果表格数据
# --- 统计表
grid_WH = "WH"  # 格子内居住工作人数数据表
grid_ID = "GRID_ID"  # WH表格中代表格子id的字段
# --- 流向表
work2HomeTable = "W2H"  # 在某格工作到在某格居住数据表
home2WorkTable = "H2W"  # 在某格居住到在某格工作数据表
workGridID = "GRID_ID_W"  # W2H、H2W两张表里代表工作地格子id的字段
homeGridID = "GRID_ID_H"  # W2H、H2W两张表里代表居住地格子id的字段
# --- 公共属性字段
WORK_NUM = "WORK_NUM"  # WH、W2H表中表示工作人数字段
HOME_NUM = "HOME_NUM"  # WH、H2W表中表示居住人数字段
# - 工作空间
arcpy.env.workspace = "C:/MData/WorkAndHome.gdb"
print("前期导入 -- 100%")
try:

    arcpy.env.overwriteOutput = True

    # 要素转点
    print("格网转点...")
    mobilePointFeature = mobileGridFeature + "2Point"  # 格网转点数据
    arcpy.FeatureToPoint_management(mobileGridFeature, mobilePointFeature, "CENTROID")
    print("格网转点 -- 100%")
    # 识别区域
    print("点区域识别...")
    identifyPointFeatures = mobilePointFeature + "IdBound"  # 识别区域后的格网点数据
    arcpy.Identity_analysis(mobilePointFeature, regionBoundaryFeature, identifyPointFeatures)
    print("点区域识别 -- 100%")
    # 添加和区域码相同的底端，表示工作格网区域码、居住格网区域码
    # Local variables:

    workRegionIDFieldStr = "WORK_ID_" + regionIDFieldStr  # 工作地区域代码字段
    homeRegionIDFieldStr = "HOME_ID_" + regionIDFieldStr  # 居住地区域代码字段
    arcpy.AddField_management(identifyPointFeatures, workRegionIDFieldStr, "TEXT")
    arcpy.AddField_management(identifyPointFeatures, homeRegionIDFieldStr, "TEXT")
    # Process: 计算字段
    calculateFieldExpression = "[" + regionIDFieldStr + "]"  # 工作、居住地区域代码均等于区域代码
    arcpy.CalculateField_management(identifyPointFeatures, workRegionIDFieldStr, calculateFieldExpression, "VB", "")
    arcpy.CalculateField_management(identifyPointFeatures, homeRegionIDFieldStr, calculateFieldExpression, "VB", "")

    # 连接统计表格与识别区域后要素图层
    print("流向数据连接要素...")

    idJoinKeepFields_Work = [workRegionIDFieldStr]
    idJoinKeepFields_Home = [homeRegionIDFieldStr]

    # 为工作地居住地流向及居住地工作地流向表格中的格网添加行政区域信息，并根据流出地-流入地（行政区域）进行汇总，得到一个流向转移矩阵
    # 分类汇总Work 2 Home
    arcpy.JoinField_management(work2HomeTable, workGridID,
                               identifyPointFeatures, identifyPointJoinField, idJoinKeepFields_Work)
    arcpy.JoinField_management(work2HomeTable, homeGridID,
                               identifyPointFeatures, identifyPointJoinField, idJoinKeepFields_Home)
    sWork2HomeFieldsList = [WORK_NUM]
    caseW2HFields = [workRegionIDFieldStr, homeRegionIDFieldStr]
    work2HomeTableSum = statsGrid.summaryStatisticsGrid2Region(work2HomeTable, sWork2HomeFieldsList, "SUM",
                                                               caseW2HFields)
    # 分类汇总Home 2 Work
    arcpy.JoinField_management(home2WorkTable, homeGridID,
                               identifyPointFeatures, identifyPointJoinField, idJoinKeepFields_Home)
    arcpy.JoinField_management(home2WorkTable, workGridID,
                               identifyPointFeatures, identifyPointJoinField, idJoinKeepFields_Work)

    sHome2WorkFieldsList = [HOME_NUM]
    caseH2WFields = [homeRegionIDFieldStr, workRegionIDFieldStr]
    home2WorkTableSum = statsGrid.summaryStatisticsGrid2Region(home2WorkTable, sHome2WorkFieldsList, "SUM",
                                                               caseH2WFields)

    # 汇总总体grid_WH 每个行政区内工作和居住的总人数
    arcpy.JoinField_management(grid_WH, grid_ID,
                               identifyPointFeatures, identifyPointJoinField, [regionIDFieldStr])
    sFieldsList = [WORK_NUM, HOME_NUM]
    caseRegionFields = [regionIDFieldStr]
    grid_WHSum = statsGrid.summaryStatisticsGrid2Region(grid_WH, sFieldsList, "SUM", caseRegionFields)

    # 将表格数据导入到SHAPE文件中
    # 生成W2H OD数组[内,外]
    statsW2HNumField = "SUM_" + WORK_NUM
    statsW2HODObj = statsGrid.statsWorkAndHomeOD(work2HomeTableSum, workRegionIDFieldStr, homeRegionIDFieldStr,
                                                 statsW2HNumField)
    # 生成H2W OD数组[内,外]
    statsH2WNumField = "SUM_" + HOME_NUM
    statsH2WODObj = statsGrid.statsWorkAndHomeOD(home2WorkTableSum, homeRegionIDFieldStr, workRegionIDFieldStr,
                                                 statsH2WNumField)
    # 计算指标
    WHBalanceQuota = statsGrid.calculateJobs_HousingBalance(regionBoundaryFeature, regionIDFieldStr,
                                                            grid_WHSum, regionIDFieldStr,
                                                            statsW2HNumField, statsH2WNumField,
                                                            statsW2HODObj, statsH2WODObj)

except Exception as err:
    print(err.args[0])
