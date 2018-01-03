# Name: MakeODCostMatrixLayer_Workflow.py
# Description: Create an origin-destination cost matrix for delivery of goods
#              from the warehouses to all stores within a 10-minute drive time
#              and save the results to a layer file on disk. Such a matrix can
#              be used as an input for logistics, delivery and routing analyses.
# Requirements: Network Analyst Extension

# Import system modules
import arcpy
from arcpy import env

try:
    # Check out the Network Analyst extension license
    arcpy.CheckOutExtension("Network")

    # Set environment settings
    env.workspace = "C:/data/Paris.gdb"
    env.overwriteOutput = True

    # Set local variables
    inNetworkDataset = "Transportation/ParisMultimodal_ND"
    outNALayerName = "WarehouseToStoreDrivetimeMatrix"
    impedanceAttribute = "Drivetime"
    searchTolerance = "1000 Meters"
    accumulateAttributeName = ["Meters"]
    inOrgins = "Analysis/Warehouses"
    inDestinations = "Analysis/Stores"
    outLayerFile = "C:/data/output" + "/" + outNALayerName + ".lyr"

    # Create a new OD Cost matrix layer. We wish to find all stores within a 10
    # minute cutoff. Apart from finding the drive time to the stores, we also
    # want to find the total distance. So we will accumulate the "Meters"
    # impedance attribute.
    outNALayer = arcpy.na.MakeODCostMatrixLayer(inNetworkDataset, outNALayerName,
                                                impedanceAttribute, 10, "",
                                                accumulateAttributeName)

    # Get the layer object from the result object. The OD cost matrix layer can
    # now be referenced using the layer object.
    outNALayer = outNALayer.getOutput(0)

    # Get the names of all the sublayers within the OD cost matrix layer.
    subLayerNames = arcpy.na.GetNAClassNames(outNALayer)
    # Stores the layer names that we will use later
    originsLayerName = subLayerNames["Origins"]
    destinationsLayerName = subLayerNames["Destinations"]

    # Load the warehouse locations as origins using a default field mappings and
    # a search tolerance of 1000 Meters.
    arcpy.na.AddLocations(outNALayer, originsLayerName, inOrgins, "",
                          searchTolerance)

    # Load the store locations as destinations and map the NOM field from stores
    # features as Name property using field mappings
    fieldMappings = arcpy.na.NAClassFieldMappings(outNALayer, destinationsLayerName)
    fieldMappings["Name"].mappedFieldName = "NOM"
    arcpy.na.AddLocations(outNALayer, destinationsLayerName, inDestinations,
                          fieldMappings, searchTolerance)

    # Solve the OD cost matrix layer
    arcpy.na.Solve(outNALayer)

    # Save the solved OD cost matrix layer as a layer file on disk with relative
    # paths
    arcpy.management.SaveToLayerFile(outNALayer, outLayerFile, "RELATIVE")

    print "Script completed successfully"

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys

    tb = sys.exc_info()[2]
    print "An error occured on line %i" % tb.tb_lineno
    print str(e)
