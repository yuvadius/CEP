'''
This is the main file of the library.
"events": 
An array of "Event" class. 
Can be set only once by the constructor
'''

import threading
from Event import *
from Pattern import *
from Algorithms import *
from Query import *

class CEP:
    def __init__(self, events: List[Event]):
        self.events = events
    
    '''
    This function receives a query and an algorithm and returns all of the found
    patterns on the events using the query and algorithm
    "query": A class "Query" that defines what patterns to look for
    "algorithm": A class "Algorithm" that defines what algorithm to use for finding the pattern
    "isThread": Boolean that decides whether to open the function in a new thread or not
    '''
    def findPattern(self, query: Query, algorithm: Algorithm, isThread: bool = False) -> Pattern:
        if isThread:
            thread = threading.Thread(target = algorithm.eval, args = (query, self.events,))
            thread.start()
            return thread
        else:
            return algorithm.eval(query, self.events)