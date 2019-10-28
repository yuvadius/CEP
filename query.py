'''
Pattern Structure is a list of qitems
Pattern Matching Condition is a formula
Sliding Window's format is to be discussed.
'''

from Formula import *
from PatternStructure import *
from typing import List

class Query:
    def __init__(self, patternStructure: PatternStructure, patternMatchingCondition: Formula = TrueFormula(), slidingWindow = None):
        self.patternStructure = patternStructure
        self.patternMatchingCondition = patternMatchingCondition
        self.slidingWindow = slidingWindow