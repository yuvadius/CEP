import threading
from Event import *

class CEP:
    def __init__(self, events):
        self.events = events

    def __findPattern(self, query):
        return 0

    def findPattern(self, query, thread = False):
        if thread:
            return threading.Thread(target = self.__findPattern, args = (query,))
        else:
            return self.__findPattern(query)

p1 = CEP(Event.fileInput("NASDAQ_20080201_1_sorted.txt"))
thread = p1.findPattern(0, True)
print(thread)