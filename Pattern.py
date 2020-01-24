'''
Pattern Structure is a PatternStructure object.
Pattern Matching Condition is a formula
Sliding Window's format is a timedelta object.
'''

from Formula import Formula
from PatternStructure import PatternStructure
from typing import List
from datetime import timedelta
from typing import List, Dict
from Utils import StatisticsTypes

class Pattern:
    def __init__(self, patternStructure: PatternStructure, patternMatchingCondition: Formula = None, slidingWindow: timedelta = timedelta.max, newOrder: List = None):
        self.patternStructure = patternStructure
        self.patternMatchingCondition = patternMatchingCondition
        self.slidingWindow = slidingWindow
        self.newOrder = newOrder
        self.statisticsType = StatisticsTypes.NO_STATISTICS
    
    def setAdditionalStatistics(self, statisticType, statistics):
        self.statisticsType = statisticType
        self.statistics = statistics