class CEP:
    def __init__(self, events):
        self.events = events

    def myfunc(self):
        print("Hello my name is " + self.events)

p1 = CEP("John")
p1.myfunc()