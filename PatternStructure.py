'''
These classes are used to represent a "parameter" to the PATTERN clause.
'''

from __future__ import annotations
from abc import ABC  # Abstract Base Class
from typing import List


class PatternStructure(ABC):
    def __init__(self):
        pass

class QItem(PatternStructure):
    def __init__(self, eventType: str, name: str):
        self.eventType = eventType
        self.name = name

class AndPatternStructure(PatternStructure):
    def __init__(self, args: List[PatternStructure]):
        self.args = args

class OrPatternStructure(PatternStructure):
    def __init__(self, args: List[PatternStructure]):
        self.args = args

class SeqPatternStructure(PatternStructure):
    def __init__(self, args: List[PatternStructure]):
        self.args = args

class KleenePlusPatternStructure(PatternStructure):
    def __init__(self, arg: PatternStructure):
        self.arg = arg

class NegationPatternStructure(PatternStructure):
    def __init__(self, arg: PatternStructure):
        self.arg = arg