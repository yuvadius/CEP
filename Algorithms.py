'''
This file contains all the pattern detection algorithms.
The abstract base class is "Algorithm".
All specific algorithm classes will inherit from the base class.
All specific algorithm classes will implement the function eval that returns
all of the patterns for a query and a set of events.
'''

from abc import ABC  # Abstract Base Class
from Query import *
from Event import *
from Pattern import *
from typing import List

class Algorithm(ABC):
    @staticmethod
    def eval(query: Query, events: List[Event]) -> Pattern:
        pass

class Tree(Algorithm):
    @staticmethod
    def eval(query: Query, events: List[Event]) -> Pattern:
        pass