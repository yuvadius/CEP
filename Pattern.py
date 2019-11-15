'''
Pattern Structure is a PatternStructure object.
Pattern Matching Condition is a formula
Sliding Window's format is a timedelta object.
'''

from Formula import *
from PatternStructure import *
from typing import List
from datetime import timedelta


class Pattern:
    def __init__(self, patternStructure: PatternStructure, patternMatchingCondition: Formula = TrueFormula(), slidingWindow: timedelta = timedelta.max):
        self.patternStructure = patternStructure
        self.patternMatchingCondition = patternMatchingCondition
        self.slidingWindow = slidingWindow