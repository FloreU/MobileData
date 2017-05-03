import datetime


def create_days_range(start_day, end_day):
    days = (datetime.datetime.strptime(end_day, "%Y-%m-%d") -
            datetime.datetime.strptime(start_day, "%Y-%m-%d")).days + 1
    days_range = []
    for i in range(days):
        temp_day = datetime.datetime.strptime(start_day, "%Y-%m-%d") + datetime.timedelta(i)
        temp_day_str = temp_day.strftime("%Y-%m-%d")
        days_range.append(temp_day_str)
    return days_range


def create_time_range(start_time, end_time, d_time_list):
    # start_time=end_time="%Y-%m-%d %H:%M:%S"
    # d_time_list=[dD,dH,dM,dS]
    start_dh_array = start_time.split(" ")
    end_dh_array = end_time.split(" ")
    start_day = start_dh_array[0]
    end_day = end_dh_array[0]
    days_range = create_days_range(start_day, end_day)
    start_hms = start_dh_array[1]
    end_hms = end_dh_array[1]
    day_num = len(days_range)
    start_hms_array = start_hms.split(":")
    end_hms_array = end_hms.split(":")
    start_time = [0, int(start_hms_array[0]), int(start_hms_array[1]), int(start_hms_array[2])]
    end_time = [(day_num - 1), int(end_hms_array[0]), int(end_hms_array[1]), int(end_hms_array[2])]
    end_time_num = end_time[0] * 10 ** 6 + end_time[1] * 10 ** 4 + end_time[2] * 10 ** 2 + end_time[3]
    current_time = start_time
    d_time_list = check_time_list(d_time_list)
    time_range = [start_time]
    while 1:
        current_time[0] = current_time[0] + d_time_list[0]
        current_time[1] = current_time[1] + d_time_list[1]
        current_time[2] = current_time[2] + d_time_list[2]
        current_time[3] = current_time[3] + d_time_list[3]
        if current_time[3] >= 60:
            current_time[3] -= 60
            current_time[2] += 1
        if current_time[2] >= 60:
            current_time[2] -= 60
            current_time[1] += 1
        if current_time[1] >= 24:
            if not (current_time[1] == 24 and current_time[2] == 0 and current_time[3] == 0):
                current_time[1] -= 24
                current_time[0] += 1
        current_time_num = (current_time[0] * 10 ** 6 +
                            current_time[1] * 10 ** 4 +
                            current_time[2] * 10 ** 2 +
                            current_time[3])
        if current_time_num <= end_time_num:
            current_hms_format = "{0}:{1}:{2}".format("{0:>02}".format(current_time[1]),
                                                      "{0:>02}".format(current_time[2]),
                                                      "{0:>02}".format(current_time[3]))
            current_time_format = days_range[current_time[0]] + " " + current_hms_format
            time_range.append(current_time_format)
        else:
            break
    return time_range


def check_time_list(time_list):
    # time_list=[D,H,M,S]
    time_list[0] = int(time_list[0])
    time_list[1] = int(time_list[1])
    time_list[2] = int(time_list[2])
    time_list[3] = int(time_list[3])
    if time_list[3] >= 60:
        d_minute = time_list[3] / 60
        time_list[3] %= 60
        time_list[2] += d_minute
    if time_list[2] >= 60:
        d_hour = time_list[2] / 60
        time_list[2] %= 60
        time_list[1] += d_hour
    if time_list[1] >= 24:
        d_day = time_list[1] / 24
        time_list[1] %= 24
        time_list[0] += d_day
    return time_list
