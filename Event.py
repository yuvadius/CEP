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

    '''
    Receives a file and returns an array of events.
    "filepath": the relative path to the file that is to be read.
    The file will be parsed as so:
    * Each line will be a different event
    * Each line will be split on "," and the resulting array will be stored in an "Event"
    '''
    @staticmethod
    def fileInput(filePath: str, eventTypeIndex: int) -> List[Event]:
        with open(filePath, "r") as f:
            content = f.readlines()
        events = []
        for i in range(len(content)):
            event = content[i].replace("\n", "").split(",")
            events.append(Event(event, event[eventTypeIndex]))
        return events