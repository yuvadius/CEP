'''
These classes are used to represent a "parameter" to the PATTERN clause.
'''

from __future__ import annotations
from abc import ABC  # Abstract Base Class
from typing import List


class PatternStructure(ABC):
    def __init__(self):
        pass

    def getTopOperator(self):
        return type(self)

class QItem(PatternStructure):
    def __init__(self, eventType: str, name: str):
        self.eventType = eventType
        self.name = name

class AndOperator(PatternStructure):
    def __init__(self, args: List[PatternStructure]):
        self.args = args

class OrOperator(PatternStructure):
    def __init__(self, args: List[PatternStructure]):
        self.args = args

class SeqOperator(PatternStructure):
    def __init__(self, args: List[PatternStructure]):
        self.args = args

class StrictSeqOperator(PatternStructure):
    def __init__(self, args: List[PatternStructure]):
        self.args = args

class KleenePlusOperator(PatternStructure):
    def __init__(self, arg: PatternStructure):
        self.arg = arg

class NegationOperator(PatternStructure):
    def __init__(self, arg: PatternStructure):
        self.arg = arg