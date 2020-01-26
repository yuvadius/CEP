'''
The "Event" class is one of the inputs expected by the "CEP" class.
The Event class has an event field which is a dictionary mapping between
field names and fields.
It also have an event type - the type which might be required in a pattern's structure,
and the timestamp of the event, which is referred to as "date".
'''

from __future__ import annotations
from typing import Dict
from datetime import datetime

class Event:
    def __init__(self, event: Dict, eventType, date: datetime):
        self.event = event
        self.eventType = eventType
        self.date = date