'''
This file contains all the pattern match detection algorithms.
The abstract base class is "Algorithm".
All specific algorithm classes will inherit from the base class.
All specific algorithm classes will implement the function eval that returns
all of the matches for a pattern and a set of events.
'''

from __future__ import annotations
from abc import ABC  # Abstract Base Class
from Pattern import *
from Event import *
from PatternMatch import *
from PatternStructure import *
from Stream import *
from typing import List

class Algorithm(ABC):
    @staticmethod
    def eval(pattern: Pattern, events: Stream, matches : Stream) -> PatternMatch:
        pass

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

    def getPatternMatch(self) -> PatternMatch:
        if (self.leafIndex < len(self.leafList)):
            return None
        events = []
        for node in self.leafList:
            events.append(node.value)
        return PatternMatch(events)

    @staticmethod
    def eval(pattern: Pattern, events: Stream, matches: Stream):
        treeList = [Tree.createTree(pattern)]
        #Strict Sequence Order
        if (type(pattern.patternStructure) == SeqPatternStructure):
            for event in events:
                # Iterate backwards(All but first) to enable element deletion while iterating
                for i in range(len(treeList) - 1, -1, -1):
                    if (i != 0 and treeList[i].addEvent(event) == False):
                        del treeList[i]
                if (treeList[0].addEvent(event) == True):
                    treeList.insert(0, Tree.createTree(pattern)) # Empty tree never removed
                for i in range(len(treeList) - 1, -1, -1):
                    patternMatch = treeList[i].getPatternMatch()
                    if (patternMatch != None):
                        matches.addItem(patternMatch)
                        del treeList[i]
        matches.end()

    @staticmethod
    def createTree(pattern: Pattern) -> Tree:
        args = pattern.patternStructure.args
        nodeList = []
        for arg in args:
            nodeList.append(TreeNode(arg))
        root = nodeList[0]
        if len(nodeList) > 1:
            root = TreeNode(None, None, nodeList[0], nodeList[1])
            if len(nodeList) > 2:
                for node in nodeList[2:]:
                    root = TreeNode(None, None, root, node)
        #print(root.valueType.eventType)
        return Tree(root, nodeList)
