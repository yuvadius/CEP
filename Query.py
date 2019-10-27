'''
Pattern Structure is a list of qitems
Pattern Matching Condition is a formula
Sliding Window's format is to be discussed.
'''

from Formula import *
from QItem import *

class Query:
    def __init__(self, patternStructure, patternMatchingCondition, slidingWindow = None):
        self.patternStructure = patternStructure
        self.patternMatchingCondition = patternMatchingCondition
        self.slidingWindow = slidingWindow