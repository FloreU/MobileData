# -*- coding: UTF-8 -*-
import arcpy
import time
import arrayMat
import re


def createG2RDict(identifyPointFeatures, gridIDFieldStr, regionIDFieldStr):
    # 获取每个格子ID与识别区域ID的对应关系字典
    # 通过格子ID找到格子属于哪个区
    startT = time.time()
    grid2RegionDict = {}
    iPFCursor = arcpy.SearchCursor(identifyPointFeatures)
    for row in iPFCursor:
        grid2RegionDict[row.getValue(gridIDFieldStr)] = row.getValue(regionIDFieldStr)
    endT = time.time()
    del iPFCursor
    print("耗时: {0} s".format(endT - startT))
    return grid2RegionDict


def getAttributeUniqueValue(inFeature, fieldStr):
    startT = time.time()
    uniqueValueList = []
    inFeatureCursor = arcpy.SearchCursor(inFeature)
    for row in inFeatureCursor:
        filedValue = row.getValue(fieldStr)
        if filedValue not in uniqueValueList:
            uniqueValueList.append(filedValue)
    endT = time.time()
    del inFeatureCursor
    print("耗时: {0} s".format(endT - startT))
    return uniqueValueList


def separateTableByFieldOneValue(tableName, filedName, filedValue, inPath="", outPath=""):
    expression = filedName + " = '" + filedValue + "'"
    newTableName = outPath + "O_" + tableName + "_" + re.sub(r'\W', "_", filedValue)
    tableName = inPath + tableName
    arcpy.TableToTable_conversion(tableName, arcpy.env.workspace, newTableName, expression)
    return newTableName


def separateTableByFieldValue(tableName, filedName, uniqueValue=None, inPath="", outPath=""):
    if uniqueValue is None:
        print("分拆表格 - 获取唯一值...")
        uniqueValue = getAttributeUniqueValue(inPath + tableName, filedName)
        print("分拆表格 - 获取唯一值 -- 100%")
    tableNameList = []
    uniqueValueLength = len(uniqueValue)
    count = 0.0
    print("分拆表格 - 分拆中 -- 0%")
    for uValue in uniqueValue:
        newTableName = separateTableByFieldOneValue(tableName, filedName, uValue, inPath, outPath)
        tableNameList.append(newTableName)
        count += 1
        print("分拆表格 - 分拆中 -- {:.2f}%".format(count / uniqueValueLength * 100))
    return tableNameList


def summaryStatisticsGrid2Region(inTable, sFieldsList, sType, regionIDField):
    stats = []
    sType = sType.upper()
    outTable = inTable + "_Stats_" + sType
    inTableFieldList = arcpy.ListFields(inTable)
    for field in inTableFieldList:
        if field.type in ("Double", "Integer", "Single", "SmallInteger"):
            if field.name in sFieldsList:
                tempS = [field.name, sType]
                stats.append(tempS)
        else:
            if (field.name in sFieldsList) and (sType in ["MIN", "MAX", "COUNT", "FIRST", "LAST"]):
                tempS = [field.name, sType]
                stats.append(tempS)
    arcpy.Statistics_analysis(inTable, outTable, stats, regionIDField)
    return outTable


def summaryAllStatisticsTable(tableNameList, sFieldsList, sType, regionIDField):
    outTableNameList = []
    tableLength = len(tableNameList)
    count = 0.0
    print("汇总表格 -- 0%")
    for tableName in tableNameList:
        outTableName = summaryStatisticsGrid2Region(tableName, sFieldsList, sType, regionIDField)
        outTableNameList.append(outTableName)
        count += 1
        print("汇总表格 -- {:.2f}%".format(count / tableLength * 100))
    return outTableNameList


def separateTableByOneDay(tableName, dateTimeFiledName, dateValue, inPath="", outPath=""):
    expression = dateTimeFiledName + " LIKE '" + dateValue + "%'"
    newTableName = outPath + "D_" + tableName + "_" + re.sub(r'\W', "_", dateValue)
    tableName = inPath + tableName
    arcpy.TableToTable_conversion(tableName, arcpy.env.workspace, newTableName, expression)
    return newTableName


def separateTableByTimeInOneDay(tableName, dateTimeFiledName, timeValue, inPath="", outPath=""):
    expression = dateTimeFiledName + " LIKE '%" + timeValue + "'"
    newTableName = outPath + "T_" + tableName + "_" + re.sub(r'\W', "_", timeValue)
    tableName = inPath + tableName
    arcpy.TableToTable_conversion(tableName, arcpy.env.workspace, newTableName, expression)
    return newTableName


def separateTableByDays(tableName, filedName, uniqueDaysValue=None, inPath="", outPath=""):
    if uniqueDaysValue is None:
        print("分拆表格 - 获取唯一日期...")
        uniqueValue = getAttributeUniqueValue(inPath + tableName, filedName)
        uniqueDaysValue = []
        for uValue in uniqueValue:
            uValueA = uValue.split(" ")
            if uValueA[0] not in uniqueDaysValue:
                uniqueDaysValue.append(uValueA[0])
        print("分拆表格 - 获取唯一日期 -- 100%")
    tableNameList = []
    uniqueValueLength = len(uniqueDaysValue)
    count = 0.0
    print("分拆表格 - 分拆中 -- 0%")
    for uDayValue in uniqueDaysValue:
        newTableName = separateTableByOneDay(tableName, filedName, uDayValue, inPath, outPath)
        tableNameList.append(newTableName)
        count += 1
        print("分拆表格 - 分拆中 -- {:.2f}%".format(count / uniqueValueLength * 100))
    return tableNameList


def separateTableByTimes(tableName, filedName, uniqueTimeValue=None, inPath="", outPath=""):
    if uniqueTimeValue is None:
        print("分拆表格 - 获取唯一时刻...")
        uniqueValue = getAttributeUniqueValue(inPath + tableName, filedName)
        uniqueTimeValue = []
        for uValue in uniqueValue:
            uValueA = uValue.split(" ")
            if uValueA[-1] not in uniqueTimeValue:
                uniqueTimeValue.append(uValueA[-1])
        print("分拆表格 - 获取唯一时刻 -- 100%")
    tableNameList = []
    uniqueValueLength = len(uniqueTimeValue)
    count = 0.0
    print("分拆表格 - 分拆中 -- 0%")
    for uTimeValue in uniqueTimeValue:
        newTableName = separateTableByTimeInOneDay(tableName, filedName, uTimeValue, inPath, outPath)
        tableNameList.append(newTableName)
        count += 1
        print("分拆表格 - 分拆中 -- {:.2f}%".format(count / uniqueValueLength * 100))
    return tableNameList


# # # 老旧的统计流向
def statsOD_old(statsODTable, gridIDField, statODField, grid2RegionDict):
    regionList = []
    for key in grid2RegionDict:
        regionName = grid2RegionDict[key]
        if regionName not in regionList:
            regionList.append(regionName)
    regionListLength = len(regionList)
    statsODArray = arrayMat.zeros(regionListLength)

    statsODTableCursor = arcpy.SearchCursor(statsODTable)
    for statsODRow in statsODTableCursor:
        gridIDFieldValue = statsODRow.getValue(gridIDField)
        if gridIDFieldValue in grid2RegionDict:
            oRegionName = grid2RegionDict[gridIDFieldValue]
            if oRegionName not in regionList:
                continue
            oRegionIndex = regionList.index(oRegionName)
            statODFieldValue = statsODRow.getValue(statODField)
            tempTODDict = translateODsInfo_old(statODFieldValue)
            for dGridID in tempTODDict:
                dRegionName = grid2RegionDict[dGridID]
                dRegionNum = tempTODDict[dGridID]
                if dRegionName not in regionList:
                    continue
                dRegionIndex = regionList.index(dRegionName)
                statsODArray[oRegionIndex][dRegionIndex] += dRegionNum
    if "" in regionList:
        regionList[regionList.index("")] = "NoneOfIdentify"
    statsODObj = {"regionList": regionList, "statsODArray": statsODArray}
    del statsODTableCursor
    return statsODObj


def translateODsInfo_old(oneODsInfoStr):
    translateODDist = {}
    oneODsInfoList = oneODsInfoStr.split(",")
    for oneODInfo in oneODsInfoList:
        if ":" in oneODInfo:
            oneODInfoList = oneODInfo.split(":")
            if oneODInfoList[1] is not "":
                translateODDist[oneODInfoList[0]] = int(oneODInfoList[1])
    return translateODDist


# # # 老旧的


# 新
def statsWorkAndHomeOD(statsODTable, originField, destinationField, numField):
    originList = []
    statsODTableCursor = arcpy.SearchCursor(statsODTable)
    for statsODRow in statsODTableCursor:
        originFieldValue = statsODRow.getValue(originField)
        if originFieldValue == '':
            originFieldValue = "otherR"
        if originFieldValue not in originList:
            originList.append(originFieldValue)
    del statsODTableCursor
    originListLength = len(originList)
    simpleODArray = arrayMat.zeros([originListLength, 2])
    statsODTableCursor = arcpy.SearchCursor(statsODTable)
    for statsODRow in statsODTableCursor:
        originFieldValue = statsODRow.getValue(originField)
        destinationFieldValue = statsODRow.getValue(destinationField)
        if originFieldValue == '':
            originFieldValue = "otherR"
        if destinationFieldValue == '':
            destinationFieldValue = "otherR"
        numFieldValue = statsODRow.getValue(numField)
        originIndex = originList.index(originFieldValue)
        if originFieldValue == destinationFieldValue:
            simpleODArray[originIndex][0] += numFieldValue
        else:
            simpleODArray[originIndex][1] += numFieldValue
    del statsODTableCursor
    statsODObj = {'originList': originList, 'simpleODArray': simpleODArray}
    return statsODObj


# 计算指标
# 居住密度：居住人口/面积 HomeDensity
# 就业密度：就业人口/面积 WorkDensity
# 职住比：为一定区域内就业岗位数与就业人口之比 Work_HomeProportion
# 居住者平衡人数：为本区块居住者中有多少人数在本区块就业 HomeInWorkPlaceNum
# 就业者平衡人数：为本区块就业者中有多少人数在本区块居住 WorkInHomePlaceNum
# 居住者平衡指数：为本区块居住者中有多少比例（占居住者）在本区块就业 HomeInWorkPlaceProportion
# 就业者平衡指数：为本区块就业者中有多少比例（占就业者）在本区块居住 WorkInHomePlaceProportion


def calculateJobs_HousingBalance(regionBoundaryFeature, regionIDFieldStr,
                                 grid_WHSumTable, grid_WHSumRegionField, grid_WHSumWorkNumField, grid_WHSumHomeNumField,
                                 statsW2HODObj, statsH2WODObj):
    regionBoundaryFeatureWithQuota = regionBoundaryFeature + "_Quota"
    arcpy.CopyFeatures_management(regionBoundaryFeature, regionBoundaryFeatureWithQuota)
    HomeDensity = "HD"
    WorkDensity = "WD"
    WorkHomeProportion = "WHP"
    HomeInWorkPlaceNum = "HWPN"
    WorkInHomePlaceNum = "WHPN"
    HomeInWorkPlaceProportion = "HWPP"
    WorkInHomePlaceProportion = "WHPP"
    arcpy.AddField_management(regionBoundaryFeatureWithQuota, HomeDensity, "DOUBLE")
    arcpy.AddField_management(regionBoundaryFeatureWithQuota, WorkDensity, "DOUBLE")
    arcpy.AddField_management(regionBoundaryFeatureWithQuota, WorkHomeProportion, "DOUBLE")
    arcpy.AddField_management(regionBoundaryFeatureWithQuota, HomeInWorkPlaceNum, "LONG")
    arcpy.AddField_management(regionBoundaryFeatureWithQuota, WorkInHomePlaceNum, "LONG")
    arcpy.AddField_management(regionBoundaryFeatureWithQuota, HomeInWorkPlaceProportion, "DOUBLE")
    arcpy.AddField_management(regionBoundaryFeatureWithQuota, WorkInHomePlaceProportion, "DOUBLE")
    # 连接就业居住总表
    keepFiledList = [grid_WHSumWorkNumField, grid_WHSumHomeNumField]
    arcpy.JoinField_management(regionBoundaryFeatureWithQuota, regionIDFieldStr,
                               grid_WHSumTable, grid_WHSumRegionField, keepFiledList)
    W2HOL = statsW2HODObj["originList"]
    W2HODA = statsW2HODObj["simpleODArray"]
    H2WOL = statsH2WODObj["originList"]
    H2WODA = statsH2WODObj["simpleODArray"]
    QuotaCursor = arcpy.UpdateCursor(regionBoundaryFeatureWithQuota)
    for row in QuotaCursor:
        regionID = row.getValue(regionIDFieldStr)
        regionArea = row.getValue("Shape_Area")
        HomeNum = row.getValue(grid_WHSumHomeNumField)
        WorkNum = row.getValue(grid_WHSumWorkNumField)
        HD = HomeNum / regionArea  # 居住密度
        WD = WorkNum / regionArea  # 就业密度
        if HomeNum == 0:
            WHP = -1
        else:
            WHP = WorkNum / HomeNum  # 职住比

        H2WAID = H2WOL.index(regionID)
        HWPN = H2WODA[H2WAID][0]  # 居住者平衡人数
        W2HAID = W2HOL.index(regionID)
        WHPN = W2HODA[W2HAID][0]  # 就业者平衡人数
        if HomeNum == 0:
            HWPP = -1
        else:
            HWPP = HWPN / HomeNum
        if WorkNum == 0:
            WHPP = -1
        else:
            WHPP = WHPN / WorkNum
        # 更新该条数据
        row.setValue(HomeDensity, HD)
        row.setValue(WorkDensity, WD)
        row.setValue(WorkHomeProportion, WHP)
        row.setValue(HomeInWorkPlaceNum, HWPN)
        row.setValue(WorkInHomePlaceNum, WHPN)
        row.setValue(HomeInWorkPlaceProportion, HWPP)
        row.setValue(WorkInHomePlaceProportion, WHPP)
        QuotaCursor.updateRow(row)
    del QuotaCursor
    return regionBoundaryFeatureWithQuota
