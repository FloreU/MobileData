# -*- coding: UTF-8 -*-
import arcpy
import statsGrid

print("前期导入 -- 100%")
try:
    arcpy.env.workspace = "C:/TestOSG.gdb"
    arcpy.env.overwriteOutput = True

    # 要素转点
    print("格网转点...")
    mobileGridFeature = "wuhan_grid"  # 划分的格网图形数据
    mobilePointFeature = mobileGridFeature + "2Point"  # 格网转点数据
    arcpy.FeatureToPoint_management(mobileGridFeature, mobilePointFeature, "CENTROID")
    print("格网转点 -- 100%")
    # 识别区域
    print("点区域识别...")
    regionBoundaryFeature = "wuhanRegionNew_84"  # 识别区域数据
    identifyPointFeatures = mobilePointFeature + "IdBound"  # 识别区域后的格网点数据
    arcpy.Identity_analysis(mobilePointFeature, regionBoundaryFeature, identifyPointFeatures)
    print("点区域识别 -- 100%")
    # 添加和区域码相同的底端，表示工作格网区域码、居住格网区域码
    # Local variables:
    regionIDFieldStr = "QQSDM"  # 区域代码字段
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
    work2HomeTable = "GRID_WORK"  # 在某格工作到在某格居住数据表
    home2WorkTable = "GRID_HOME"  # 在某格居住到在某格工作数据表
    grid_WH = "GRID_WH"  # 格子内居住工作人数数据表
    workGridID = "GRID_ID_W"
    homeGridID = "GRID_ID_H"
    grid_ID = "GRID_ID"
    identifyPointJoinField = "grid_id"
    idJoinKeepFields_Work = [workRegionIDFieldStr]
    idJoinKeepFields_Home = [homeRegionIDFieldStr]
    WORK_NUM = "WORK_NUM"
    HOME_NUM = "HOME_NUM"

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
                                                            grid_WHSum, regionIDFieldStr, WORK_NUM, HOME_NUM,
                                                            statsW2HODObj, statsH2WODObj)

except Exception as err:
    print(err.args[0])
