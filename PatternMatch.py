'''
This class's instances are the output results of an evaluation mechanism's eval function.
It has one field which is the list of events in the pattern match.
'''

from Event import Event
from typing import List

class PatternMatch:
    def __init__(self, events: List[Event]):
        self.events = events