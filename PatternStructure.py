'''
These classes are used to represent a "parameter" to the PATTERN clause.
'''

from __future__ import annotations
from abc import ABC  # Abstract Base Class
from typing import List

class QItem:
    def __init__(self, eventType: str, name: str, kleenePlus: bool = False, negated: bool = False):
        self.eventType = eventType
        self.name = name # Don't think that this is necessary
        self.kleenePlus = kleenePlus
        self.negated = negated

class PatternStructure(ABC):
    def __init__(self, qitems: List[QItem]):
        self.qitems = qitems

# Strict Order
class StrictSequencePatternStructure(PatternStructure):
    def __init__(self, qitems: List[QItem]):
        super(StrictSequencePatternStructure, self).__init__(qitems)