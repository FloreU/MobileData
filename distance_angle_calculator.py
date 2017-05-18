# -*- coding: UTF-8 -*-
import math
import arcgisHelper as ah



class DistanceAngelCalculator:
    def __init__(self, table_name, grid_point_info):
        self.table_name = table_name
        self.field_px = grid_point_info["x"]
        self.field_py = grid_point_info["y"]
        self.field_name_gid = grid_point_info["id"]
        self.field_name_tpw = grid_point_info["tpw"]
        self.field_name_tph = grid_point_info["tph"]
        self.grid_point_table = grid_point_info["grid_table"]
        self.__create_point_dict__()

    def __create_point_dict__(self):
        point_rows = ah.get_rows(self.grid_point_table)
        point_id_dict = {}
        for row in point_rows:
            point_id = row.getValue(self.field_name_gid)
            point_x = row.getValue(self.field_px)
            point_y = row.getValue(self.field_py)
            point_id_dict[point_id] = {self.field_px: point_x, self.field_py: point_y}
        self.point_id_dict = point_id_dict

    def __get_distance__(self, i1, i2):
        point1 = self.point_id_dict[i1]
        point2 = self.point_id_dict[i2]
        if point1[self.field_px] == point2[self.field_px] and point1[self.field_py] == point2[self.field_py]:
            return 112.1010
        return math.sqrt(
            (point1[self.field_px] - point2[self.field_px]) ** 2 + (point1[self.field_py] - point2[self.field_py]) ** 2)

    def __get_angle__(self, id1, id2):
        def __angle__(dy, dx):
            if dy == 0 and dx == 0:
                return -1
            m_angle = math.atan2(dy, dx)
            if m_angle < 0:
                m_angle += 2 * math.pi
            return m_angle
        point1 = self.point_id_dict[id1]
        point2 = self.point_id_dict[id2]
        p1_x = point1[self.field_px]
        p2_x = point2[self.field_px]
        p1_y = point1[self.field_py]
        p2_y = point2[self.field_py]
        dtx = p2_x - p1_x
        dty = p2_y - p1_y
        return __angle__(dty, dtx)

    def __get_route__(self, i1, i2):
        point1 = self.point_id_dict[i1]
        point2 = self.point_id_dict[i2]
        return [[point1[self.field_px], point1[self.field_py]], [point2[self.field_px], point2[self.field_py]]]


def calculate(table_name, grid_point_info, todo):

    field_name_distance = "DISTANCE"
    field_name_angle = "ANGLE"
    dac = DistanceAngelCalculator(table_name, grid_point_info)

    # 生成0~2Pi大小的数字表征方向，同一网格到同一网格值为-1
    def __angle_h2w__(row):
        id1 = row.getValue(dac.field_name_tph)
        id2 = row.getValue(dac.field_name_tpw)
        return dac.__get_angle__(id1, id2)

    def __angle_w2h__(row):
        id1 = row.getValue(dac.field_name_tpw)
        id2 = row.getValue(dac.field_name_tph)
        return dac.__get_angle__(id1, id2)

    # 生成以m为单位的距离
    def __distance__(row):
        id1 = row.getValue(dac.field_name_tpw)
        id2 = row.getValue(dac.field_name_tph)
        return dac.__get_distance__(id1, id2)

    f_dict = {
        "d": [__distance__, field_name_distance],
        "w2h": [__angle_w2h__, field_name_angle],
        "h2w": [__angle_h2w__, field_name_angle],
    }

    ah.calculate_fields(dac.table_name, [f_dict[t][0] for t in todo], [f_dict[t][1] for t in todo])


def get_all_route_h2w(table_name, grid_point_info, class_list, file_name):
    dac = DistanceAngelCalculator(table_name, grid_point_info)
    rows = ah.get_rows(table_name)
    result = [[] for _ in xrange(5)]
    num = 0
    for row in rows:
        num += 1
        if num % 100 == 0:
            print "process on", num
        id1 = row.getValue(dac.field_name_tph)
        id2 = row.getValue(dac.field_name_tpw)
        value = row.getValue("HOME_NUM")
        for index, item in enumerate(class_list):
            if value <= item:
                if index - 1 < 0:
                    break
                result[index - 1].append(dac.__get_route__(id1, id2))
                break
    f = open(file_name, "w")
    f.write(str(result))
    f.close()


def get_all_route_w2h(table_name, grid_point_info, class_list, file_name):
    dac = DistanceAngelCalculator(table_name, grid_point_info)
    rows = ah.get_rows(table_name)
    result = [[] for _ in xrange(5)]
    num = 0
    for row in rows:
        num += 1
        if num % 100 == 0:
            print "process on", num
        id1 = row.getValue(dac.field_name_tpw)
        id2 = row.getValue(dac.field_name_tph)
        value = row.getValue("WORK_NUM")
        for index, item in enumerate(class_list):
            if value <= item:
                if index - 1 < 0:
                    break
                result[index - 1].append(dac.__get_route__(id1, id2))
                break
    f = open(file_name, "w")
    f.write("var allData = " + str(result))
    f.close()


def get_region_fields(table_name, region_field, region_id, return_fields):
    where_clause = '"' + region_field + '"=\'' + str(region_id) + '\''
    rows = ah.get_rows(table_name, where_clause)
    return [[row.getValue(field) for field in return_fields] for row in rows]


def get_qx_director_scatter(table_name, region_field):

    qx_list = ah.qx_list
    result = {}
    for qbm in qx_list:
        where_clause = \
            '"' + region_field + '"=\'' + str(qbm) + '\'' + " AND " + '"ANGLE" > 0' + " AND " + '"HOME_NUM" >= 10 '
        rows = ah.get_rows(table_name, where_clause)
        qx_values = []
        for row in rows:
            num = row.getValue("HOME_NUM")
            distance = row.getValue("DISTANCE") / 1000.0
            angle = row.getValue("ANGLE") / (math.pi * 2) * 360
            qx_values.append([distance, angle, num])
        result[ah.region_dict(qbm)] = qx_values

    f = open("QX_DA_NUM.js", "w")
    f.write("var allData =" + str(result) + ";")
    f.close()



    


def main():
    ah.set_env("E:/InformationCenter/TestGDB.gdb", True)
    get_qx_director_scatter("H2W", "H_QBM")

    # 提取grid级别的route数据
    # get_all_route_w2h("W2H",
    #         {"grid_table": "POINTS_P", "x": "PX", "y": "PY", "id": "grid_id", "tpw": "GRID_ID_W", "tph": "GRID_ID_H"},
    #         [10, 80, 240, 550, 1200, 1000000])
    # 提取街道级别的route数据
    # get_all_route_h2w("H2W_Stats_SUM_191",
    #         {"grid_table": "BOUND_191_WGS84_POINT", "x": "PX", "y": "PY", "id": "JBM", "tpw": "W_JBM", "tph": "H_JBM"},[10, 1300, 7200, 20000, 42300, 80000], "jd_route.js")
    # 提取区县级别的route数据
    # get_all_route_h2w("H2W_Stats_SUM_17",
    #                   {"grid_table": "BOUND_17_WGS84_POINT", "x": "PX", "y": "PY", "id": "QBM", "tpw": "WORK_ID_QBM",
    #                    "tph": "HOME_ID_QBM"},[10, 11110, 41200, 83500, 216700, 500000], "qx_route.js")

if __name__ == '__main__':
    main()
