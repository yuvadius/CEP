'''
The "Event" class is one of the inputs expected by the "CEP" class.
It has one variable "__event".
"__event" is an array of values.
It is the users responsibility to know what the values in "__event" stand for.
Note: "__event" might me changed in the future to a dictionary"
'''

class Event:
    def __init__(self, event):
        self.event = event

    '''
    Receives a file and returns an array of events.
    "filepath": the relative path to the file that is to be read.
    The file will be parsed as so:
    * Each line will be a different event
    * Each line will be split on "," and the resulting array will be stored in an "Event"
    '''
    @staticmethod
    def fileInput(filePath):
        with open(filePath, "r") as f:
            content = f.readlines()
        events = []
        for i in range(len(content)): 
            events.append(Event(content[i].replace("\n", "").split(",")))
        return events