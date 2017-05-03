# -*- coding: UTF-8 -*-
# 生成多维数组
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def objMats(inObj, dList, kD=0):
    if kD == (len(dList) - 1):
        cLength = dList[kD]
        oMat = []
        for i in range(cLength):
            oMat.append(inObj)
        return oMat
    else:
        cLength = dList[kD]
        oMat = []
        newKD = kD + 1
        for i in range(cLength):
            oMat.append(objMats(inObj, dList, newKD))
        return oMat


def zeros(num):
    arrayList = []
    if isinstance(num, int):
        num = int(abs(num))
        for i in range(num):
            tempA = []
            for j in range(num):
                tempA.append(0)
            arrayList.append(tempA)
    elif isinstance(num, list):
        arrayList = objMats(0, num)
    return arrayList


def ones(num):
    arrayList = []
    if isinstance(num, int):
        num = int(abs(num))
        for i in range(num):
            tempA = []
            for j in range(num):
                tempA.append(1)
            arrayList.append(tempA)
    elif isinstance(num, list):
        arrayList = objMats(1, num)
    return arrayList


def nones(num):
    arrayList = []
    if isinstance(num, int):
        num = int(abs(num))
        for i in range(num):
            tempA = []
            for j in range(num):
                tempA.append(None)
            arrayList.append(tempA)
    elif isinstance(num, list):
        arrayList = objMats(None, num)
    return arrayList
