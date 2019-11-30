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
from typing import Dict
from datetime import date, datetime, timedelta

class Algorithm(ABC):
    @staticmethod
    def eval(pattern: Pattern, events: Stream, matches : Stream) -> PatternMatch:
        pass

class TreeNode:
    def __init__(self, valueType: QItem, value: Event = None, left: TreeNode = None, right: TreeNode = None, parent: TreeNode = None, formula: Formula = None):
        self.valueType = valueType
        self.value = value
        self.left = left
        self.right = right
        self.parent = parent
        self.formula = formula

    def isLeaf(self):
        return (self.left == None and self.right == None)

    def evaluate(self, evalDictionary: Dict):
        if self.formula == None:
            return True
        return self.formula.eval(evalDictionary)

class Tree(Algorithm):
    def __init__(self, root: TreeNode, leafList: List[TreeNode], maxTimeDelta: timedelta = timedelta.max):
        self.root = root
        self.leafList = leafList
        self.leafIndex = 0
        self.maxTimeDelta = maxTimeDelta
        self.minTime = None
        self.maxTime = None

    def getEvaluationDictionary(self, evaluationDictionary = {}):
        for i in range(0, self.leafIndex):
            evaluationDictionary[self.leafList[i].valueType.name] = self.leafList[i].value.event
        return evaluationDictionary

    def addEvent(self, event: Event) -> bool:
        currentLeaf = self.leafList[self.leafIndex]
        minTime = event.date if (self.minTime == None) else min(self.minTime, event.date)
        maxTime = event.date if (self.maxTime == None) else max(self.maxTime, event.date)
        if(currentLeaf.valueType.eventType != event.eventType):
            return False
        if(currentLeaf.evaluate(event) == False):
            return False
        if(self.leafIndex > 0 and currentLeaf.parent.formula != None and currentLeaf.parent.evaluate(self.getEvaluationDictionary({currentLeaf.valueType.name: event.event})) == False):
            return False
        if(self.maxTimeDelta != timedelta.max and minTime + self.maxTimeDelta < maxTime):
            return False
        self.minTime = minTime
        self.maxTime = maxTime
        currentLeaf.value = event
        self.leafIndex += 1
        return True

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
        if (type(pattern.patternStructure) == StrictSeqPatternStructure):
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
        #Adding the sequences to the tree
        nodeList = []
        for arg in pattern.patternStructure.args:
            nodeList.append(TreeNode(arg))
        root = nodeList[0]
        if len(nodeList) > 1:
            root = TreeNode(None, None, nodeList[0], nodeList[1])
            nodeList[0].parent = root
            nodeList[1].parent = root
            if len(nodeList) > 2:
                for node in nodeList[2:]:
                    prevRoot = root
                    root = TreeNode(None, None, prevRoot, node)
                    prevRoot.parent = root
                    node.parent = root
        #Adding the formulas to the tree
        if len(nodeList) == 1:
            nodeList[0].formula = pattern.patternMatchingCondition
        else:
            formulas = Formula.splitAndFormulas(pattern.patternMatchingCondition)
            for formula in formulas:
                identifiers = Formula.getIdentifiers(formula)
                if len(identifiers) == 1:
                    for node in nodeList:
                        if node.valueType.name == identifiers[0]:
                            node.formula = formula
                            break
                elif len(identifiers) > 1:
                    nodeIdentifiers = []
                    for node in nodeList:
                        if node.valueType.name in identifiers:
                            nodeIdentifiers.append(node.valueType.name)
                            if len(identifiers) == len(nodeIdentifiers):
                                node.parent.formula = formula
                                break
        return Tree(root, nodeList, pattern.slidingWindow)
