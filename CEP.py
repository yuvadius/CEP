'''
This is the main file of the library.
"events": 
An array of "Event" class. 
Can be set only once by the constructor
'''

import threading
from Event import *
from PatternMatch import *
from TreeBasedEvaluation import *
from TreeBasedAlgorithms import *
from OrderBasedAlgorithms import *
from Pattern import *
from Utils import *

class CEP:
    '''
    This function receives a pattern and an algorithm
    pattern matches on the events using the pattern and algorithm
    "pattern": A class "Pattern" that defines what patterns to look for
    "algorithm": A class "Algorithm" that defines what algorithm to use for finding the pattern
    '''
    def __init__(self, algorithm: type, patterns: List[Pattern] = None, events: Stream = None, output: Container = None, saveReplica: bool = True):
        self.eventStreams = []
        self.patternMatches = output if output else Stream()
        self.algorithm = algorithm
        self.elapsed = [None]
        if saveReplica and events:
            self.baseStream = events
        elif saveReplica:
            self.baseStream = Stream()
        else:
            self.baseStream = None
        
        if patterns:
            for pattern in patterns:
                eventStream = self.baseStream.duplicate() if self.baseStream else Stream()
                worker = threading.Thread(target = self.algorithm.eval, args = (pattern, eventStream, self.patternMatches))
                worker.start()
                self.eventStreams.append(eventStream)

    def getElapsed(self):
        return self.elapsed[0]

    def addEvent(self, event: Event):
        for eventStream in self.eventStreams: 
            eventStream.addItem(event)
        if self.baseStream:
            self.baseStream.addItem(event)
    
    def addPattern(self, pattern: Pattern, priority: int = 0, policy : PolicyType = PolicyType.FIND_ALL):
        eventStream = self.baseStream.duplicate() if self.baseStream else Stream()
        worker = threading.Thread(target = self.algorithm.eval, args = (pattern, eventStream, self.patternMatches))
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
