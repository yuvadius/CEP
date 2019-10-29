'''
This file contains all the pattern detection algorithms.
The abstract base class is "Algorithm".
All specific algorithm classes will inherit from the base class.
All specific algorithm classes will implement the function eval that returns
all of the patterns for a query and a set of events.
'''

from __future__ import annotations
from abc import ABC  # Abstract Base Class
from Query import *
from Event import *
from Pattern import *
from PatternStructure import *
from typing import List

class Algorithm(ABC):
    @staticmethod
    def eval(query: Query, events: List[Event]) -> Pattern:
        pass

    @staticmethod
    def fileOutput(patterns: List[Pattern]):
        with open('patterns.txt', 'w') as f:
            for pattern in patterns:
                for event in pattern.events:
                    f.write("%s\n" % event.event)
                f.write("\n" % event.event)

class TreeNode:
    def __init__(self, valueType: QItem, value: Event = None, left: TreeNode = None, right: TreeNode = None, parent: TreeNode = None):
        self.valueType = valueType
        self.value = value
        self.left = left
        self.right = right
        self.parent = parent

    def isLeaf(self):
        return (self.left == None and self.right == None)

class Tree(Algorithm):
    def __init__(self, root: TreeNode, leafList: List[TreeNode]):
        self.root = root
        self.leafList = leafList
        self.leafIndex = 0

    def addEvent(self, event: Event) -> bool:
        if(self.leafList[self.leafIndex].valueType.eventType == event.eventType):
            self.leafList[self.leafIndex].value = event
            self.leafIndex += 1
            return True
        return False

    def getPattern(self) -> Pattern:
        if (self.leafIndex < len(self.leafList)):
            return None
        events = []
        for node in self.leafList:
            events.append(node.value)
        return Pattern(events)

    @staticmethod
    def eval(query: Query, events: List[Event]):
        patterns = [] # List of patterns that will be returned
        treeList = [Tree.createTree(query)]
        #Strict Sequence Order
        if (type(query.patternStructure) == StrictSequencePatternStructure):
            for event in events:
                # Iterate backwards(All but first) to enable element deletion while iterating
                for i in range(len(treeList) - 1, -1, -1):
                    if (i != 0 and treeList[i].addEvent(event) == False):
                        del treeList[i]
                if (treeList[0].addEvent(event) == True):
                    treeList.insert(0, Tree.createTree(query)) # Empty tree never removed
                for i in range(len(treeList) - 1, -1, -1):
                    pattern = treeList[i].getPattern()
                    if (pattern != None):
                        patterns.append(pattern)
                        del treeList[i]
        Algorithm.fileOutput(patterns)

    @staticmethod
    def createTree(query: Query) -> Tree:
        qitems = query.patternStructure.qitems
        nodeList = []
        for qitem in qitems:
            nodeList.append(TreeNode(qitem))
        root = nodeList[0]
        if len(nodeList) > 1:
            root = TreeNode(None, None, nodeList[0], nodeList[1])
            if len(nodeList) > 2:
                for node in nodeList[2:]:
                    root = TreeNode(None, None, root, node)
        #print(root.valueType.eventType)
        return Tree(root, nodeList)
