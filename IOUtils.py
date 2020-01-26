from __future__ import annotations
from typing import List
from Event import Event
from IODataStructures import Stream, Container
from Utils import stringToNumber
from datetime import datetime

'''
Receives a file and returns a stream of events.
"filepath": the path to the file that is to be read.
The file will be parsed as so:
* Each line will be a different event
* Each line will be split on "," and the resulting array will be stored in an "Event",
  and the keys are determined from the given list "KeyMap".
'''
def fileInput(filePath: str, keyMap: List, eventTypeKey: str, eventTimeKey: str) -> Stream:
    with open(filePath, "r") as f:
        content = f.readlines()
    events = Stream()
    for i in range(len(content)):
        eventLine = content[i].replace("\n", "").split(",")
        for j in range(len(eventLine)):
            eventLine[j] = stringToNumber(eventLine[j])
        # Create the fields of an event object.
        event = dict(zip(keyMap, eventLine))
        eventType = event[eventTypeKey]
        eventTime = datetime(year=int(str(event[eventTimeKey])[0:4]), month=int(str(event[eventTimeKey])[4:6]), day=int(str(event[eventTimeKey])[6:8]), hour=int(str(event[eventTimeKey])[8:10]), minute=int(str(event[eventTimeKey])[10:12]))
        # Add the event to the stream according to created field.
        events.addItem(Event(event, eventType, eventTime))
    events.close()
    return events

'''
Writes output matches to a file in the subfolder "Matches".
It supports any iterable as output matches.
'''
def fileOutput(matches, fileOutputName: str = 'matches.txt'):
    with open("Matches/" + fileOutputName, 'w') as f:
        for match in matches:
            for event in match.events:
                f.write("%s\n" % event.event)
            f.write("\n")