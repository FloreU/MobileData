# -*- coding: UTF-8 -*-
import arcpy
from arcpy import mapping

mxd = arcpy.mapping.MapDocument(r"C:\Workspace\wuhan.mxd")
for lyr in arcpy.mapping.ListLayers(mxd):
  if lyr.symbologyType == "GRADUATED_COLORS":
    lyr.symbology.valueField = "Shape_Leng"
    lyr.symbology.numClasses = 5
mxd.saveACopy("wuhan1.mxd")
del mxd


# import arcpy
# from arcpy import mapping
#
# blank_mxd_path = r"C:\blank_mxd.mxd"
# mxd = arcpy.mapping.MapDocument(blank_mxd_path)
# df = arcpy.mapping.ListDataFrames(mxd)[0]
#
# shapefile_path = r"C:\path\to\file.shp"
# arcpy.MakeFeatureLayer_management(shapefile_path, "nameinTOC")
# layer = arcpy.mapping.Layer("nameinTOC")
# arcpy.mapping.AddLayer(df, layer, "AUTO_ARRANGE")
#
# mxd.saveACopy(r"C:\location\of\your\new\mapDoc.mxd")
#
# del mxd