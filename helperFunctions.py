from __future__ import annotations
from enum import Enum

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

class addEventErrors(Enum):
    SUCCESS = 0
    WRONG_EVENT_TYPE_ERROR = 1
    NOT_WITHIN_TIMESCALE_ERROR = 2
    EVALUATION_ERROR = 3