'''
This is the main file of the library.
"events": 
An array of "Event" class. 
Can be set only once by the constructor
'''

import threading
from Event import Event
from PatternMatch import PatternMatch
from IODataStructures import Stream, Container
from Pattern import Pattern
from typing import List
from EvaluationMechanism import EvaluationMechanism

# A sketch of QoS specifications
class PerformanceSpecifications:
    def __init__(self, memoryLimit, constructionTimeLimit, **kwargs):
        pass

class CEP:
    '''
    This function receives a pattern and an algorithm
    pattern matches on the events using the pattern and algorithm
    "pattern": A class "Pattern" that defines what patterns to look for
    "algorithm": A class "Algorithm" that defines what algorithm to use for finding the pattern
    '''
    def __init__(self, algorithm: EvaluationMechanism, patterns: List[Pattern] = None, events: Stream = None, output: Container = None, saveReplica: bool = True, performanceSpecs : PerformanceSpecifications = None):
        if algorithm.isMultiplePatternCompatible():
            raise NotImplementedError()
        # Otherwise, every pattern is handled separately.
        self.eventStreams = []
        self.patternMatches = output if output else Stream()
        self.algorithmObjects = {}
        self.algorithm = algorithm
        if saveReplica and events:
            self.baseStream = events
        elif saveReplica:
            self.baseStream = Stream()
        else:
            self.baseStream = None
        
        if patterns:
            for pattern in patterns:
                eventStream = self.baseStream.duplicate() if self.baseStream else Stream()
                self.algorithmObjects[pattern] = algorithm.copy()
                worker = threading.Thread(target = self.algorithmObjects[pattern].eval, args = (pattern, eventStream, self.patternMatches, True))
                worker.start()
                self.eventStreams.append(eventStream)

    def getElapsed(self, pattern):
        return self.algorithmObjects[pattern].getElapsed()

    def addEvent(self, event: Event):
        for eventStream in self.eventStreams: 
            eventStream.addItem(event)
        if self.baseStream:
            self.baseStream.addItem(event)
    
    def addPattern(self, pattern: Pattern, priority: int = 0):
        if pattern in self.algorithmObjects.keys():
            return # pattern is already evaluated.
        eventStream = self.baseStream.duplicate() if self.baseStream else Stream()
        self.algorithmObjects[pattern] = self.algorithm.copy()
        worker = threading.Thread(target = self.algorithmObjects[pattern].eval, args = (pattern, eventStream, self.patternMatches))
        worker.start()
        self.eventStreams.append(eventStream)
    
    def getPatternMatch(self):
        try:
            return self.patternMatches.getItem()
        except StopIteration:
            return None
    
    def getPatternMatchContainer(self):
        return self.patternMatches

    def close(self):
        for eventStream in self.eventStreams:
            eventStream.close()
        if self.baseStream:
            self.baseStream.close()
