class Event:
    def __init__(self, event):
        self.__event = event

    def getEvent(self):
        return self.__event

    @staticmethod
    def fileInput(filePath):
        with open(filePath, "r") as f:
            content = f.readlines()
        events = []
        for i in range(len(content)): 
            events.append(Event(content[i].replace("\n", "").split(",")))
        return events