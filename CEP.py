import Event

class CEP:
    def __init__(self, events):
        self.events = events

    def myfunc(self):
        print("Hello my name is " + self.events[0].event[0])

p1 = CEP(Event.Event.fileInput("NASDAQ_20080201_1_sorted.txt"))
p1.myfunc()