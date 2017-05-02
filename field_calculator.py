# -*- coding: UTF-8 -*-
import arcgisHelper as ah


# 执行主函数
# 工作空间中的表格名字 table_name
# 处理函数的列表 functions
# 处理结果字段名字的列表 result_fields
# 辅助的变量 aux
def execute_calculator(table_name, functions, result_fields, field_type="DOUBLE"):
    # table_rows = get_update_rows(t_name)
    for f, r in zip(functions, result_fields):
        print "on processing ", f.__name__
        # table_rows.reset()
        ah.add_field(r, field_type, table_name)
        table_rows = ah.get_update_rows(table_name)
        calculator_rows(table_rows, f, r)
        del table_rows


def calculator_rows(rows, function, result_field_name):
    for row in rows:
        result = function(row)
        ah.add_field_value(result, result_field_name, row, rows)
