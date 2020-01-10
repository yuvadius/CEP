
from abc import ABC
from queue import Queue

# represents a container of objects. Dedicated to matches, but can be implemented by a stream.
# The container can only have items added to it and pulled out from. You can add items until you
# close the container.
class Container(ABC):
    def addItem(self, item):
        pass

    def getItem(self):
        pass

    # somehow has to note that the item
    def close(self):
        pass

class Stream(Container):
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
    
    def close(self):
        self.stream.put(None)
    
    def duplicate(self):
        ret = Stream()
        ret.stream.queue = self.stream.queue.copy()
        return ret
    
    def getItem(self):
        return self.__next__()
    
    def count(self):
        return self.stream.qsize()
    
    def first(self):
        return self.stream.queue[0]
    
    def last(self):
        x = self.stream.queue[-1]  
        if not x: # if stream is closed last is None. We need the one before None.
            x = self.stream.queue[-2]
        return x   