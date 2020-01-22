from __future__ import annotations
from Event import *
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Dict
from PatternStructure import QItem
from random import randint
from itertools import combinations
from PatternStructure import SeqOperator
from PatternMatch import PatternMatch
from copy import deepcopy

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

class StatisticsTypes(Enum):
    NO_STATISTICS = 0
    FREQUENCY_DICT = 1
    SELECTIVITY_MATRIX_AND_ARRIVAL_RATES = 2

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

# Entire CEP algorithm in a couple lines of code(inefficient)
# This will be used as our test creater
def generateMatches(pattern, stream):
    args = pattern.patternStructure.args
    types = {qitem.eventType for qitem in args}
    isSeq = (pattern.patternStructure.getTopOperator() == SeqOperator)
    events = {}
    matches = []
    for event in stream:
        if event.eventType in types:
            if event.eventType in events.keys():
                events[event.eventType].append(event)
            else:
                events[event.eventType] = [event]
    generateMatchesRecursive(pattern, events, isSeq, [], datetime.max, datetime.min, matches, {})
    return matches

def generateMatchesRecursive(pattern, events, isSeq, match, minEventDate, maxEventDate, matches, binding, loop = 0):
    patternLength = len(pattern.patternStructure.args)
    if loop == patternLength:
        if pattern.patternMatchingCondition.eval(binding):
            if not doesMatchExist(matches, match):
                matches.append(PatternMatch(deepcopy(match)))
    else:
        qitem = pattern.patternStructure.args[loop]
        for event in events[qitem.eventType]:
            minDate = min(minEventDate, event.date)
            maxDate = max(maxEventDate, event.date)
            binding[qitem.name] = event.event
            if maxDate - minDate <= pattern.slidingWindow:
                if not isSeq or len(match) == 0 or match[-1].date <= event.date:
                    match.append(event)
                    generateMatchesRecursive(pattern, events, isSeq, match, minDate, maxDate, matches, binding, loop + 1)
                    del match[-1]
        del binding[qitem.name]

def doesMatchExist(matches, match):
    for match2 in matches:
        if len(match) == len(match2.events):
            isEqual = True
            for i in range(len(match)):
                if match[i] != match2.events[i]:
                    isEqual = False
                    break
            if isEqual:
                return True
    return False 
