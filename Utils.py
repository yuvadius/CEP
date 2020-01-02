from __future__ import annotations
from enum import Enum
from typing import List, Dict

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

class AddEventErrors(Enum):
    SUCCESS = 0
    WRONG_EVENT_TYPE_ERROR = 1
    NOT_WITHIN_TIMESCALE_ERROR = 2
    LAZY_BEFORE_LEFT_NODE = 3
    LAZY_AFTER_RIGHT_NODE = 4
    EVALUATION_ERROR = 5

class OrderType(Enum):
    ORDERED = 0
    NOT_ORDERED = 1
    LAZY_ORDERED = 2

class PolicyType(Enum):
    FIND_ALL = 0
    FIND_FAST = 1