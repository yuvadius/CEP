from Formula import Formula
from PatternStructure import PatternStructure
from typing import List
from datetime import timedelta
from typing import List, Dict
from Utils import StatisticsTypes

'''
A pattern has several fields:
Pattern Structure is a PatternStructure object.
Pattern Matching Condition is a Formula object.
Sliding Window is a timedelta object.
The above three are used to represent a PATTERN WHERE WITHIN clause, i.e. a SASE pattern.
A pattern can also carry statistics with it, in order to enable advanced
tree construction mechanisms.
'''
class Pattern:
    def __init__(self, patternStructure: PatternStructure, patternMatchingCondition: Formula = None, slidingWindow: timedelta = timedelta.max, newOrder: List = None):
        self.patternStructure = patternStructure
        self.patternMatchingCondition = patternMatchingCondition
        self.slidingWindow = slidingWindow
        self.newOrder = newOrder
        self.statisticsType = StatisticsTypes.NO_STATISTICS
    
    def setAdditionalStatistics(self, statisticType : StatisticsTypes, statistics):
        self.statisticsType = statisticType
        self.statistics = statistics