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
from helperFunctions import *

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
    def recursiveEvaluation(self, evalDictionary: Dict, nodesEvaluated: List[TreeNode]):
        if self.evaluation == True:
            return True if self.parent == None else self.parent.recursiveEvaluation(evalDictionary, nodesEvaluated)
        #If sons evaluated to true
        elif (self.left == None or self.left.evaluation) and (self.right == None or self.right.evaluation):
            self.evaluation = True if (self.formula == None) else self.formula.eval(evalDictionary)
            if (self.evaluation == False):
                return False
            else:
                nodesEvaluated.append(self)
            if (self.parent == None):#At top
                return True
            return self.parent.recursiveEvaluation(evalDictionary, nodesEvaluated)
        else:
            return True

class Tree(Algorithm):
    def __init__(self, root: TreeNode, leafList: List[TreeNode], maxTimeDelta: timedelta = timedelta.max, minTime: datetime = None, maxTime: datetime = None, evaluationDictionary: Dict = {}, leafIndex: int = 0, isEmpty: bool = True):
        self.root = root
        self.leafList = leafList
        self.leafIndex = leafIndex
        self.maxTimeDelta = maxTimeDelta
        self.minTime = minTime
        self.maxTime = maxTime
        self.evaluationDictionary = evaluationDictionary
        self.isEmpty = isEmpty

    def addEvent(self, event: Event, treeCopy: List[Tree] = None) -> bool:
        currentLeaf = self.leafList[self.leafIndex]
        minTime = event.date if (self.minTime == None) else min(self.minTime, event.date)
        maxTime = event.date if (self.maxTime == None) else max(self.maxTime, event.date)
        if(self.maxTimeDelta != timedelta.max and minTime + self.maxTimeDelta < maxTime):
            return addEventErrors.NOT_WITHIN_TIMESCALE_ERROR
        if(currentLeaf.valueType.eventType != event.eventType):
            return addEventErrors.WRONG_EVENT_TYPE_ERROR
        self.evaluationDictionary[currentLeaf.valueType.name] = event.event
        nodesEvaluated = []
        if(currentLeaf.recursiveEvaluation(self.evaluationDictionary, nodesEvaluated) == False):
            del self.evaluationDictionary[currentLeaf.valueType.name]
            return addEventErrors.EVALUATION_ERROR
        if (treeCopy != None):
            # Undo tree changes for the copy
            for node in nodesEvaluated:
                node.evaluation = False
            del self.evaluationDictionary[currentLeaf.valueType.name]
            treeCopy.append(self.copy())
            # Redo tree changes after the copy
            for node in nodesEvaluated:
                node.evaluation = True
            self.evaluationDictionary[currentLeaf.valueType.name] = event.event
        self.minTime = minTime
        self.maxTime = maxTime
        currentLeaf.value = event
        self.leafIndex += 1
        self.isEmpty = False
        return addEventErrors.SUCCESS

    def getPatternMatch(self) -> PatternMatch:
        if (self.root.evaluation == False):
            return None
        events = []
        for node in self.leafList:
            events.append(node.value)
        return PatternMatch(events)

    def getCurrentEventType(self) -> str:
        return self.leafList[self.leafIndex].valueType.eventType

    def copy(self) -> Tree:
        leafList = self.leafList[:self.leafIndex]
        root = self.root.copyNodes(None, leafList)
        return Tree(root, leafList, self.maxTimeDelta, self.minTime, self.maxTime, deepcopy(self.evaluationDictionary), self.leafIndex, self.isEmpty)

    @staticmethod
    def eval(pattern: Pattern, events: Stream, matches: Stream):
        # Strict Sequence Order
        if (pattern.patternStructure.getTopOperator() == StrictSeqOperator):
            emptyTree = Tree.createLeftDeepTree(pattern)
            treeList = [emptyTree.copy()]
            for event in events:
                # Iterate backwards to enable element deletion while iterating
                for i in range(len(treeList) - 1, -1, -1):
                    isEmpty = treeList[i].isEmpty
                    addEventStatus = treeList[i].addEvent(event)
                    if (isEmpty == False and addEventStatus != addEventErrors.SUCCESS):
                        del treeList[i]
                    elif (addEventStatus == addEventErrors.SUCCESS):
                        patternMatch = treeList[i].getPatternMatch()
                        if (patternMatch != None):
                            matches.addItem(patternMatch)
                            del treeList[i]
                        if (isEmpty == True):
                            treeList.append(emptyTree.copy()) # Empty tree never removed
        # Sequence Order
        elif (pattern.patternStructure.getTopOperator() == SeqOperator):
            # Sort trees in dict based on their next incoming eventType
            treeDict = {}
            for qItem in pattern.patternStructure.args:
                treeDict[qItem.eventType] = []
            firstEventType = pattern.patternStructure.args[0].eventType
            treeDict[firstEventType].append(Tree.createLeftDeepTree(pattern))
            for event in events:
                currentEventType = event.eventType
                if currentEventType in treeDict: # Ignore events that or not in Sequence
                    # Iterate backwards to enable element deletion while iterating
                    for i in range(len(treeDict[currentEventType]) - 1, -1, -1):
                        copiedTree = []
                        currentTree = treeDict[currentEventType][i]
                        addEventStatus = currentTree.addEvent(event, copiedTree)
                        if (addEventStatus == addEventErrors.NOT_WITHIN_TIMESCALE_ERROR):
                            del treeDict[currentEventType][i] # Will not be the empty tree
                        elif (addEventStatus == addEventErrors.SUCCESS):
                            treeDict[currentEventType].append(copiedTree[0]) # Add copy to end
                            patternMatch = currentTree.getPatternMatch()
                            if (patternMatch != None):
                                matches.addItem(patternMatch)
                            else:
                                nextEventType = currentTree.getCurrentEventType()
                                treeDict[nextEventType].append(currentTree)
                            del treeDict[currentEventType][i]
        matches.end()

    @staticmethod
    def createLeftDeepTree(pattern: Pattern) -> Tree:
        #Adding the sequences to the tree
        nodeList = []
        for qItem in pattern.patternStructure.args:
            nodeList.append(TreeNode(qItem))
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
