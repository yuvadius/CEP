from __future__ import annotations
from Event import *
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Dict
from PatternStructure import QItem
from random import randint
from itertools import combinations

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
    
    tempList = [(i, occurences[qitems[i].eventType]) for i in range(len(qitems))]
    tempList = sorted(tempList, key=lambda x: x[1])
    ret = [i[0] for i in tempList]
    return ret

def getAllDisjointSets(s : frozenset):
    if len(s) == 2:
        yield (frozenset({t}) for t in s)
        return
    
    first = next(iter(s))
    for i in range(len(s) - 1):
        for c in combinations(s.difference({first}), i):
            set1 = frozenset(c).union({first})
            set2 = s.difference(set1)
            yield (set1, set2)


def findAllTreeTopologies(s : frozenset):
    if len(s) == 1:
        yield tuple(s)[0]
        return
    if len(s) == 2:
        yield tuple(s)
        return
    
    for set1, set2 in getAllDisjointSets(s):
        for topology1 in findAllTreeTopologies(set1):
            for topology2 in findAllTreeTopologies(set2):
                yield (topology1, topology2)


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

def merge(arr1, arr2, key=lambda x: x):
    newLen = len(arr1) + len(arr2)
    ret = []
    i = i1 = i2 = 0
    while i < newLen and i1 < len(arr1) and i2 < len(arr2):
        if key(arr1[i1]) < key(arr2[i2]):
            ret.append(arr1[i1])
            i1 += 1
        else:
            ret.append(arr2[i2])
            i2 += 1
        i += 1
    
    while i1 < len(arr1):
        ret.append(arr1[i1])
        i1 += 1
    
    while i2 < len(arr2):
        ret.append(arr2[i2])
        i2 += 1
    
    return ret

def mergeAccordingTo(arr1, arr2, actual1, actual2, key=lambda x: x):
    if len(arr1) != len(actual1) or len(arr2) != len(actual2):
        raise Exception()

    newLen = len(arr1) + len(arr2)
    ret = []
    i = i1 = i2 = 0
    while i < newLen and i1 < len(arr1) and i2 < len(arr2):
        if key(arr1[i1]) < key(arr2[i2]):
            ret.append(actual1[i1])
            i1 += 1
        else:
            ret.append(actual2[i2])
            i2 += 1
        i += 1
    
    while i1 < len(arr1):
        ret.append(actual1[i1])
        i1 += 1
    
    while i2 < len(arr2):
        ret.append(actual2[i2])
        i2 += 1
    
    return ret

def isSorted(arr, key=lambda x: x):
    if len(arr) == 0:
        return True
    
    for i in range(len(arr) - 1):
        if key(arr[i]) > key(arr[i + 1]):
            return False
    
    return True

def buildTreeFromOrder(order):
    ret = order[0]
    for i in range(1, len(order)):
        ret = (ret, order[i])
    return ret
