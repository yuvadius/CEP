'''
Pattern Structure is a list of qitems
Pattern Matching Condition is a formula
Sliding Window's format is to be discussed.
'''

from Formula import *
from QItem import *

class Query:
    def __init__(self, patternStructure, patternMatchingCondition, slidingWindow):
        self.__patternStructure = patternStructure
        self.__patternMatchingCondition = patternMatchingCondition
        self.__slidingWindow = slidingWindow

    def getPatternStructure(self):
        return self.__patternStructure
        
    def getPatternMatchingCondition(self):
        return self.__patternMatchingCondition
        
    def getSlidingWIndow(self):
        return self.__slidingWindow