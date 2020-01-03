'''
The "Event" class is one of the inputs expected by the "CEP" class.
It has one variable "__event".
"__event" is an array of values.
It is the users responsibility to know what the values in "__event" stand for.
Note: "__event" might me changed in the future to a dictionary"
'''

from __future__ import annotations
from typing import List
from datetime import datetime

class Event:
    def __init__(self, event: List, eventType: str, date: datetime, counter: int):
        self.event = event
        self.eventType = eventType
        self.date = date
        self.counter = counter # Must be unique, If 2 dates are equal than the smaller counter is the event that came first