from __future__ import annotations
from Event import *
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Dict
from PatternStructure import QItem
from random import randint

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

class IterativeImprovementType(Enum):
    SWAP_BASED = 0
    CIRCLE_BASED = 1

def swapGenerator(n : int):
    for i in range(n - 1):
        for j in range(i + 1, n):
            yield (i, j)

def circleGenerator(n : int):
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            for k in range(j + 1, n):
                yield (i,j,k)
                yield (i,k,j)

def getRandomOrder(n : int):
    order = []
    left = list(range(n))

    while len(left) > 0:
        index = randint(0, len(left) - 1)
        order.append(left[index])
        del left[index]
    
    return order

def swapper(order, move):
    i, j = move
    swap(order, i, j)

def circler(order, move):
    i,j,k = move
    tmp = order[i]
    order[i] = order[j]
    order[j] = order[k]
    order[k] = tmp

def reverseCircle(move):
    i, j, k = move
    return (k, j, i)