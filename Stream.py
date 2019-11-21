
from queue import Queue

class Stream:
    def __init__(self):
        self.stream = Queue()

    def __next__(self):
        nextItem = self.stream.get(block=True)  # Blocking get 
        if nextItem == None:
            raise StopIteration()
        return nextItem
    
    def __iter__(self):
        return self

    def addItem(self, item):
        self.stream.put(item)
    
    def end(self):
        self.stream.put(None)
    
    def duplicate(self):
        ret = Stream()
        ret.stream.queue = self.stream.queue.copy()
        return ret