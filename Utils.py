from __future__ import annotations
from Event import *
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Dict
from PatternStructure import QItem

# Return index of the closest event
def binarySearchClosestEvent(lst: List[Event], dateSearch: datetime):
    min = 0
    max = len(lst)-1
    avg = int((min+max)/2)
    while (min < max):
        if (lst[avg].date == dateSearch):
            return avg
        elif (lst[avg].date < dateSearch):
            return avg + 1 + binarySearchClosestEvent(lst[avg+1:], dateSearch)
        else:
            return binarySearchClosestEvent(lst[:avg], dateSearch)
    return avg

def isfloat(x: str):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x: str):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

def stringToNumber(x: str):
    if isint(x):
        return int(x)
    elif isfloat(x):
        return float(x)
    else:
        return x

def swap(list: List, index1: int, index2: int):
    temp = list[index1]
    list[index1] = list[index2]
    list[index2] = temp

def getOrderByOccurences(qitems: List[QItem], occurences):
    ret = list(range(len(qitems)))
    for j in range(len(qitems) - 1, -1, -1):
        for i in range(j):
            if occurences[qitems[i].eventType] > occurences[qitems[i + 1].eventType]:
                swap(ret, i, i + 1)
    return ret

class StatisticsTypes(Enum):
    NO_STATISTICS = 0
    FREQUENCY_DICT = 1
    SELECTIVITY_MATRIX_AND_ARRIVAL_RATES = 2

class AddEventErrors(Enum):
    SUCCESS = 0
    WRONG_EVENT_TYPE_ERROR = 1
    NOT_WITHIN_TIMESCALE_ERROR = 2
    LAZY_BEFORE_LEFT_NODE = 3
    LAZY_AFTER_RIGHT_NODE = 4
    EVALUATION_ERROR = 5

class OrderType(Enum):
    TRIVIAL_ORDERED = 0
    NOT_ORDERED = 1
    NONTRIVIAL_ORDERED = 2

class PolicyType(Enum):
    FIND_ALL = 0
    FIND_FAST = 1