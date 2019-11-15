'''
The "Event" class is one of the inputs expected by the "CEP" class.
It has one variable "__event".
"__event" is an array of values.
It is the users responsibility to know what the values in "__event" stand for.
Note: "__event" might me changed in the future to a dictionary"
'''

from __future__ import annotations
from typing import List

class Event:
    def __init__(self, event: List, eventType: str):
        self.event = event
        self.eventType = eventType