# -*- coding: UTF-8 -*-


def readCSInfo(path_str):
    cs_file = open(path_str, "r")
    cs_result = list()
    for line in cs_file.readlines():
        itemlist = line.split('|')
        cs_result.append(itemlist)
    cs_file.close()
    return cs_result


def readCSInfoIntoArray(path_str):
    import numpy as np
    cs_type = np.dtype({
        'names': ['MSISDN', 'IMSI', 'MCC', 'MNC',
                  'IMEI_TAC', 'First_LAC', 'First_CI',
                  'Start_time', 'Current_LAC', 'Current_CI',
                  'End_time', 'Cell_Technology_id', 'Event_type',
                  'Province_id', 'Day_id', 'Month_id'],
        'formats': ['S32', 'S32', 'S10', 'S10',
                    'S32', 'S32', 'S32',
                    'S14', 'S32', 'S32',
                    'S14', 'S1', 'S2',
                    'S3', 'S2', 'S6']})
    cs_result = np.array([], dtype=cs_type)
    cs_file = open(path_str, "r")
    for line in cs_file.readlines():
        itemlist = line.split('|')
        cs_result.append(itemlist)
    cs_file.close()
    return cs_result
