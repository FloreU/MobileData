import datetime


def createDaysRange(startDay, endDay):
    days = (datetime.datetime.strptime(endDay, "%Y-%m-%d") -
            datetime.datetime.strptime(startDay, "%Y-%m-%d")).days + 1
    daysRange = []
    for i in range(days):
        tempDay = datetime.datetime.strptime(startDay, "%Y-%m-%d") + datetime.timedelta(i)
        tempDayStr = tempDay.strftime("%Y-%m-%d")
        daysRange.append(tempDayStr)
    return daysRange


def createTimeRange(startTime, endTime, dTimeList):
    # startTime=endTime="%Y-%m-%d %H:%M:%S"
    # dTimeList=[dD,dH,dM,dS]
    startTA = startTime.split(" ")
    endTA = endTime.split(" ")
    startDay = startTA[0]
    endDay = endTA[0]
    daysRange = createDaysRange(startDay, endDay)
    startHMS = startTA[1]
    endHMS = endTA[1]
    dayNum = len(daysRange)
    startHMSA = startHMS.split(":")
    endHMSA = endHMS.split(":")
    STA = [0, int(startHMSA[0]), int(startHMSA[1]), int(startHMSA[2])]
    ETA = [(dayNum - 1), int(endHMSA[0]), int(endHMSA[1]), int(endHMSA[2])]
    CTA = STA
    dTimeList = checkTimeList(dTimeList)
    TimeRange = [startTime]
    while 1:
        CTA[0] = CTA[0] + dTimeList[0]
        CTA[1] = CTA[1] + dTimeList[1]
        CTA[2] = CTA[2] + dTimeList[2]
        CTA[3] = CTA[3] + dTimeList[3]
        if CTA[3] >= 60:
            CTA[3] -= 60
            CTA[2] += 1
        if CTA[2] >= 60:
            CTA[2] -= 60
            CTA[1] += 1
        if CTA[1] >= 24:
            if not (CTA[1] == 24 and CTA[2] == 0 and CTA[3] == 0):
                CTA[1] -= 24
                CTA[0] += 1
        currentTimeNum = CTA[0] * 10 ** 6 + CTA[1] * 10 ** 4 + CTA[2] * 10 ** 2 + CTA[3]
        endTimeNum = ETA[0] * 10 ** 6 + ETA[1] * 10 ** 4 + ETA[2] * 10 ** 2 + ETA[3]
        if currentTimeNum <= endTimeNum:
            currentHMS = "{0:>02}".format(CTA[1]) + ":" + "{0:>02}".format(CTA[2]) + ":" + "{0:>02}".format(CTA[3])
            currentTime = daysRange[CTA[0]] + " " + currentHMS
            TimeRange.append(currentTime)
        else:
            break
    return TimeRange


def checkTimeList(timeList):
    # timeList=[D,H,M,S]
    timeList[0] = int(timeList[0])
    timeList[1] = int(timeList[1])
    timeList[2] = int(timeList[2])
    timeList[3] = int(timeList[3])
    if timeList[3] >= 60:
        dM = timeList[3] / 60
        timeList[3] %= 60
        timeList[2] += dM
    if timeList[2] >= 60:
        dH = timeList[2] / 60
        timeList[2] %= 60
        timeList[1] += dH
    if timeList[1] >= 24:
        dD = timeList[1] / 24
        timeList[1] %= 24
        timeList[0] += dD
    return timeList
