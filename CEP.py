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

class CEP:
    '''
    This function receives a pattern and an algorithm
    pattern matches on the events using the pattern and algorithm
    "pattern": A class "Pattern" that defines what patterns to look for
    "algorithm": A class "Algorithm" that defines what algorithm to use for finding the pattern
    '''
    def __init__(self, algorithm: Algorithm, patterns: List[Pattern], events: Stream = None):
        if events:
            self.events = events
        else:
            self.events = Stream()
        self.patternMatches = Stream()
        self.worker = threading.Thread(target = algorithm.eval, args = (patterns[0], self.events, self.patternMatches))
        self.worker.start()
    
    def addEvent(self, event: Event):
        self.events.addItem(event)
    
    def getPatternMatch(self):
        try:
            return next(self.patternMatches)
        except StopIteration:
            return None
    
    def getPatternMatchStream(self):
        return self.patternMatches