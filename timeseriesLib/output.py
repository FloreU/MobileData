# -*- coding: UTF-8 -*-
# 生成各个属性工作日、均值均值时间线
import sys

import arcpy

from timeseriesLib import timeseries

reload(sys)
sys.setdefaultencoding('utf-8')

arcpy.env.overwriteOutput = True
out_gdb = "E:/InformationCenter/SUM_AGE.gdb"
out_path = "E:/InformationCenter/TimeLine"
timeseries.output_gdb_xls(out_gdb, out_path)
