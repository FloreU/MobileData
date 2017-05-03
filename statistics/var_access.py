# -*- coding: UTF-8 -*-
import pickle
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def save_var(var, file_path):
    out_file = open(file_path, 'wb')
    pickle.dump(var, out_file)
    out_file.close()
    return


def save_all(var_list, file_path):
    out_file = open(file_path, 'wb')
    for var in var_list:
        pickle.dump(var, out_file)
    out_file.close()
    return


def load_var(file_path):
    pkl_file = open(file_path, 'rb')
    data = pickle.load(pkl_file)
    pkl_file.close()
    return data


def load_all(file_path, var_name=[]):
    pkl_file = open(file_path, 'rb')
    count = 0
    var_obj = {}
    while 1:
        try:
            data = pickle.load(pkl_file)
            if count < len(var_name):
                var_obj[var_name[count]] = data
            else:
                var_obj[("data" + str(count))] = data
        except Exception as err:
            err[0]
            print(u"load done!")
            break
        count += 1
    pkl_file.close()
    return var_obj


def save_json(var_json, file_path):
    out_file = open(file_path, 'w')
    var_json_str = json.dumps(var_json)
    out_file.writelines(var_json_str)
    out_file.close()
    return


def load_json(file_path):
    json_file = open(file_path, 'r')
    json_line = json_file.readlines()
    if len(json_line) == 1:
        for line in json_line:
            json_data = json.loads(line)
    else:
        json_data = []
        for line in json_line:
            tmp_data = json.loads(line)
            json_data.append(tmp_data)
    json_file.close()
    return json_data


def main():
    return


if __name__ == "__main__":
    main()
