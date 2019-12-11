'''
This is the main file of the library.
"events": 
An array of "Event" class. 
Can be set only once by the constructor
'''

import threading
from Event import *
from PatternMatch import *
from Algorithms import *
from Pattern import *
from Utils import *

class CEP:
    '''
    This function receives a pattern and an algorithm
    pattern matches on the events using the pattern and algorithm
    "pattern": A class "Pattern" that defines what patterns to look for
    "algorithm": A class "Algorithm" that defines what algorithm to use for finding the pattern
    '''
    def __init__(self, algorithm: Algorithm, patterns: List[Pattern] = None, events: Stream = None):
        self.eventStreams = []
        self.patternMatches = Stream()
        self.algorithm = algorithm
        if events:
            self.baseStream = events
        else:
            self.baseStream = Stream()
        if patterns:
            for pattern in patterns:
                eventStream = self.baseStream.duplicate()
                worker = threading.Thread(target = self.algorithm.eval, args = (pattern, eventStream, self.patternMatches))
                worker.start()
                self.eventStreams.append(eventStream)

    def addEvent(self, event: Event):
        for eventStream in self.eventStreams: 
            eventStream.addItem(event)
        self.baseStream.addItem(event)
    
    def addPattern(self, pattern: Pattern, priority: int = 0, policy : PolicyType = PolicyType.FIND_ALL):
        eventStream = self.baseStream.duplicate()
        worker = threading.Thread(target = self.algorithm.eval, args = (pattern, eventStream, self.patternMatches))
        worker.start()
        self.eventStreams.append(eventStream)
    
    def getPatternMatch(self):
        try:
            return next(self.patternMatches)
        except StopIteration:
            return None
    
    def getPatternMatchStream(self):
        return self.patternMatches

    def close(self):
        for eventStream in self.eventStreams:
            eventStream.end()
        self.baseStream.end()