import threading
from Event import *
from Query import *
from Pattern import *

class CEP:
    def __init__(self, events):
        self.events = events

    def __findPattern(self, query, algorithim):
        return Pattern(Event([]))

    def findPattern(self, query, algorithim, thread = False):
        if thread:
            thread = threading.Thread(target = self.__findPattern, args = (query, algorithim,))
            thread.start()
            return thread
        else:
            return self.__findPattern(query, algorithim)

p1 = CEP(Event.fileInput("NASDAQ_20080201_1_sorted.txt"))
thread = p1.findPattern(0, 0, True)