'''
This class is the returned result of an Algorithms eval function
"time": The amount of time it took to callculate the pattern match in milliseconds.
If the time is "-1" then it can be considered as undefined
'''

from Event import *
from typing import List

class PatternMatch:
    def __init__(self, events: List[Event], time: int = -1):
        self.events = events
        self.time = time