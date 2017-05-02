# -*- coding: UTF-8 -*-

import unittest
import testDistance as td
import arcpy
import distance_angle_calculator as dac


class TestDict(unittest.TestCase):

    def test_has_fields(self):
        arcpy.env.workspace = td.env_path
        field1 = arcpy.ListFields(td.table_name_2_test)
        self.assertIn("DISTANCE", [f.name for f in field1])
        self.assertIn("ANGLE", [f.name for f in field1])

        field2 = [f.name for f in arcpy.ListFields("BOUND_17_H2W_DS")]
        # self.assertIn("Distance_1", field2)
        # self.assertIn("Volume_1", field2)
        # self.assertIn("Distance_9", field2)
        # self.assertIn("Volume_9", field2)
        # self.assertIn("Distance_16", field2)
        # self.assertIn("Volume_16", field2)

    def test_distance(self):
        arcpy.env.workspace = td.env_path
        rows = arcpy.SearchCursor(td.table_name_2_test)
        row = rows.next()
        value1 = row.getValue("DISTANCE")
        self.assertTrue(abs(float(value1) - 608.093363) < 0.01)
        row = rows.next()
        value2 = row.getValue("DISTANCE")
        self.assertTrue(abs(float(value2) - 1286.862614) < 0.01)

    def test_angle(self):
        arcpy.env.workspace = td.env_path
        rows = arcpy.SearchCursor(td.table_name_2_test)
        row = rows.next()
        value1 = row.getValue("ANGLE")
        self.assertTrue(abs(float(value1) - 5.503353) < 0.001)

        row = rows.next()
        value2 = row.getValue("ANGLE")
        self.assertTrue(abs(float(value2) - 4.715161) < 0.001)

    def test_angle_summarize(self):
        pass
        # arcpy.env.workspace = td.env_path
        # rows2 = arcpy.SearchCursor("BOUND_17_H2W_DS")
        # row = rows2.next()
        # value1 = row.getValue("Distance_1")
        # value2 = row.getValue("Volume_16")
        # value3 = row.getValue("N")
        # self.assertTrue(abs(float(value1) - 4667.148141) < 0.001)
        # self.assertTrue(abs(float(value2) - 846) < 0.001)
        # self.assertTrue(abs(float(value3) - 1478) < 0.001)

    def test_last(self):
        resume()


def resume():
    print 'tearDown...'
    arcpy.env.workspace = td.env_path
    arcpy.DeleteFeatures_management("BOUND_17_H2W_DS")
    for field_name in ["ANGLE", "DISTANCE"]:
        arcpy.DeleteField_management(td.table_name_2_test, field_name)
    print 'tearDown done'

if __name__ == '__main__':
    dac.main()
    unittest.main()
    resume()

