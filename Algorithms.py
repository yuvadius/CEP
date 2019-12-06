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
from typing import List, Dict
from datetime import date, datetime, timedelta
from copy import deepcopy

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
        self.evaluation = False

    def isLeaf(self):
        return (self.left == None and self.right == None)

    def addLeftNode(self, left):
        self.left = left
        if left != None:
            left.parent = self

    def addRightNode(self, right):
        self.right = right
        if right != None:
            right.parent = self

    def addNodes(self, left, right):
        self.addLeftNode(left)
        self.addRightNode(right)

    def copyNodes(self, parentNode: TreeNode, leafList: List[TreeNode]) -> TreeNode:
        if (self.evaluation):
            return self
        left = None if self.left == None else self.left.copyNodes(self, leafList)
        right = None if self.right == None else self.right.copyNodes(self, leafList)
        node = TreeNode(self.valueType, self.value, None, None, None, self.formula)
        node.addNodes(left, right)
        if (left == None and right == None):
            leafList.append(node)
        return node

    #Evalute node from bottom to top recursively
    def recursiveEvaluation(self, evalDictionary: Dict):
        if self.evaluation == True:
            return True if self.parent == None else self.parent.recursiveEvaluation(evalDictionary)
        #If sons evaluated to true
        elif (self.left == None or self.left.evaluation) and (self.right == None or self.right.evaluation):
            self.evaluation = True if (self.formula == None) else self.formula.eval(evalDictionary)
            if (self.evaluation == False):
                return False
            if (self.parent == None):#At top
                return True
            return self.parent.recursiveEvaluation(evalDictionary)
        else:
            return True

class Tree(Algorithm):
    def __init__(self, root: TreeNode, leafList: List[TreeNode], maxTimeDelta: timedelta = timedelta.max, minTime: datetime = None, maxTime: datetime = None, evaluationDictionary: Dict = {}, leafIndex: int = 0):
        self.root = root
        self.leafList = leafList
        self.leafIndex = leafIndex
        self.maxTimeDelta = maxTimeDelta
        self.minTime = minTime
        self.maxTime = maxTime
        self.evaluationDictionary = evaluationDictionary

    def addEvent(self, event: Event) -> bool:
        currentLeaf = self.leafList[self.leafIndex]
        minTime = event.date if (self.minTime == None) else min(self.minTime, event.date)
        maxTime = event.date if (self.maxTime == None) else max(self.maxTime, event.date)
        if(currentLeaf.valueType.eventType != event.eventType):
            return False
        if(self.maxTimeDelta != timedelta.max and minTime + self.maxTimeDelta < maxTime):
            return False
        self.evaluationDictionary[currentLeaf.valueType.name] = event.event
        if(currentLeaf.recursiveEvaluation(self.evaluationDictionary) == False):
            del self.evaluationDictionary[currentLeaf.valueType.name]
            return False
        self.minTime = minTime
        self.maxTime = maxTime
        currentLeaf.value = event
        self.leafIndex += 1
        return True

    def getPatternMatch(self) -> PatternMatch:
        if (self.root.evaluation == False):
            return None
        events = []
        for node in self.leafList:
            events.append(node.value)
        return PatternMatch(events)

    def copy(self) -> Tree:
        leafList = self.leafList[:self.leafIndex]
        root = self.root.copyNodes(None, leafList)
        return Tree(root, leafList, self.maxTimeDelta, self.minTime, self.maxTime, deepcopy(self.evaluationDictionary), self.leafIndex)

    @staticmethod
    def eval(pattern: Pattern, events: Stream, matches: Stream):
        #Strict Sequence Order
        if (pattern.patternStructure.getTopOperator() == StrictSeqOperator):
            emptyTree = Tree.createLeftDeepTree(pattern)
            treeList = [emptyTree.copy()]
            for event in events:
                # Iterate backwards to enable element deletion while iterating
                for i in range(len(treeList) - 1, 0, -1):
                    if (treeList[i].addEvent(event) == False):
                        del treeList[i]
                    else:
                        patternMatch = treeList[i].getPatternMatch()
                        if (patternMatch != None):
                            matches.addItem(patternMatch)
                            del treeList[i]
                if (treeList[0].addEvent(event)):
                    patternMatch = treeList[0].getPatternMatch()
                    if (patternMatch != None):
                        matches.addItem(patternMatch)
                        del treeList[0]
                    treeList.insert(0, emptyTree.copy()) # Empty tree never removed
        matches.end()

    @staticmethod
    def createLeftDeepTree(pattern: Pattern) -> Tree:
        #Adding the sequences to the tree
        nodeList = []
        for arg in pattern.patternStructure.args:
            nodeList.append(TreeNode(arg))
        root = nodeList[0]
        if len(nodeList) > 1:
            root = TreeNode(None, None)
            root.addNodes(nodeList[0], nodeList[1])
            if len(nodeList) > 2:
                for node in nodeList[2:]:
                    prevRoot = root
                    root = TreeNode(None, None)
                    root.addNodes(prevRoot, node)
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
