# -*- coding: UTF-8 -*-
import math
import arcgisHelper as ah
import field_calculator as fc


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

    fc.execute_calculator(dac.table_name, [f_dict[t][0] for t in todo], [f_dict[t][1] for t in todo])


def main():
    ah.set_env("C:/MData/TestGDB.gdb", True)
    calculate("H2W_TEST",
              {"grid_table": "POINTS", "x": "PX", "y": "PY", "id": "grid_id", "tpw": "GRID_ID_W", "tph": "GRID_ID_H"},
              ["d", "h2w"])

if __name__ == '__main__':
    main()
