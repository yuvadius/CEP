'''
Pattern Structure is a list of qitems
Pattern Matching Condition is a formula
Sliding Window's format is to be discussed.
'''

from Formula import *
from QItem import *
from typing import List

class Query:
    def __init__(self, patternStructure: List[QItem], patternMatchingCondition: Formula, slidingWindow = None):
        self.patternStructure = patternStructure
        self.patternMatchingCondition = patternMatchingCondition
        self.slidingWindow = slidingWindow