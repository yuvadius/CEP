'''
This file contains all the pattern detection algorithms.
The abstract base class is "Algorithm".
All specific algorithm classes will inherit from the base class.
All specific algorithm classes will implement the function eval that returns
all of the patterns for a query and a set of events.
'''

from abc import ABC  # Abstract Base Class

class Algorithm(ABC):
    def eval(self, query, events):
        pass

class Tree(Algorithm):
    def eval(self, query, events):
        pass