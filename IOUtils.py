'''
This module contains functions used as utilities to handle IO:
such as creating an event stream for a file, writing pattern stream to a file, etc.
'''

from __future__ import annotations
from typing import List
from Event import *
from Stream import *

'''
Receives a file and returns an array of events.
"filepath": the relative path to the file that is to be read.
The file will be parsed as so:
* Each line will be a different event
* Each line will be split on "," and the resulting array will be stored in an "Event"
'''
def fileInput(filePath: str, eventTypeIndex: int) -> Stream:
    with open(filePath, "r") as f:
        content = f.readlines()
    events = Stream()
    for i in range(len(content)):
        event = content[i].replace("\n", "").split(",")
        events.addItem(Event(event, event[eventTypeIndex]))
    events.end()
    return events


def fileOutput(matches: Stream):
    with open('matches.txt', 'w') as f:
        for match in matches:
            for event in match.events:
                f.write("%s\n" % event.event)
            f.write("\n" % event.event)