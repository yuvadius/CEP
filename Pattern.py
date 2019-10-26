'''
This class is the returned result of an Algorithms eval function
"time": The amount of time it took to callculate the pattern in milliseconds.
If the time is "-1" then it can be considered as undefined
'''

class Pattern:
    def __init__(self, events, time = -1):
        self.__events = events
        self.__time = time

    def getPattern(self):
        return self.__events