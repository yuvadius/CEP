'''
These classes are used to represent a "parameter" to the PATTERN clause.
'''

from abc import ABC  # Abstract Base Class
from __future__ import annotations
from typing import List

class QItem:
    def __init__(self, eventType: str, name: str, kleenePlus: bool = False, negated: bool = False):
        self.eventType = eventType
        self.name = name
        self.kleenePlus = kleenePlus
        self.negated = negated


class PatternStructure(ABC):
    def __init__(self, qitems: List[QItem]):
        self.qitems = qitems


class SequencePatternStructure(PatternStructure):
    def __init__(self, qitems: List[QItem]):
        Base.__init__(self, qitems)