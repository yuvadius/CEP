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
from IODataStructures import *
from typing import List, Dict
from datetime import date, datetime, timedelta
from copy import deepcopy
from Utils import *

class Algorithm(ABC):
    @staticmethod
    def eval(pattern: Pattern, events: Stream, matches : Container) -> PatternMatch:
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
    def recursiveEvaluation(self, evalDictionary: Dict, nodesToEvaluate: List[TreeNode], previousEvaluatedNode: TreeNode = None):
        if self.evaluation == True:
            return True if self.parent == None else self.parent.recursiveEvaluation(evalDictionary, nodesToEvaluate)
        #If sons evaluated to true
        elif (self.left == None or self.left.evaluation or self.left is previousEvaluatedNode) and (self.right == None or self.right.evaluation or self.right is previousEvaluatedNode):
            evaluation = True if (self.formula == None) else self.formula.eval(evalDictionary)
            if (evaluation == False):
                return False
            else:
                nodesToEvaluate.append(self)
            if (self.parent == None):#At top
                return True
            return self.parent.recursiveEvaluation(evalDictionary, nodesToEvaluate, self)
        else:
            return True

class Tree(Algorithm):
    def __init__(self, root: TreeNode, order: OrderType, leafList: List[TreeNode], eventTypeToLeafDict: Dict = None, maxTimeDelta: timedelta = None, minTime: datetime = None, maxTime: datetime = None, evaluationDictionary: Dict = None, leafIndex: int = 0, isEmpty: bool = True, evaluatedLeaves: List[TreeNode] = None):
        self.root = root
        self.order = order
        self.leafList = leafList
        self.maxTimeDelta = maxTimeDelta if maxTimeDelta != None else timedelta.max
        self.minTime = minTime
        self.maxTime = maxTime
        self.evaluationDictionary = evaluationDictionary if evaluationDictionary != None else {}
        self.leafIndex = leafIndex
        self.isEmpty = isEmpty
        self.eventTypeToLeafDict = eventTypeToLeafDict
        self.evaluatedLeaves = evaluatedLeaves if evaluatedLeaves != None else []

    def getCurrentLeaf(self, event: Event) -> TreeNode:
        if(self.order == OrderType.ORDERED):
            return self.leafList[self.leafIndex]
        elif(self.order == OrderType.NOT_ORDERED):
            return self.leafList[self.eventTypeToLeafDict[event.eventType][0]]
        else:
            return None

    def addEvent(self, event: Event, treeCopy: List[Tree] = None) -> bool:
        currentLeaf = self.getCurrentLeaf(event)
        minTime = event.date if (self.minTime == None) else min(self.minTime, event.date)
        maxTime = event.date if (self.maxTime == None) else max(self.maxTime, event.date)
        if(self.maxTimeDelta != timedelta.max and minTime + self.maxTimeDelta < maxTime):
            return AddEventErrors.NOT_WITHIN_TIMESCALE_ERROR
        if(currentLeaf.valueType.eventType != event.eventType):
            return AddEventErrors.WRONG_EVENT_TYPE_ERROR
        self.evaluationDictionary[currentLeaf.valueType.name] = event.event # Tree change, make sure to delete before copy or failure
        nodesToEvaluate = []
        if(currentLeaf.recursiveEvaluation(self.evaluationDictionary, nodesToEvaluate) == False):
            del self.evaluationDictionary[currentLeaf.valueType.name]
            return AddEventErrors.EVALUATION_ERROR
        if (treeCopy != None):
            # Undo tree changes for the copy
            del self.evaluationDictionary[currentLeaf.valueType.name]
            treeCopy.append(self.copy())
            # Redo tree changes after the copy
            self.evaluationDictionary[currentLeaf.valueType.name] = event.event
        for node in nodesToEvaluate:
            node.evaluation = True
        self.minTime = minTime
        self.maxTime = maxTime
        currentLeaf.value = event
        self.leafIndex += 1
        self.evaluatedLeaves.append(currentLeaf)
        self.isEmpty = False
        del self.eventTypeToLeafDict[event.eventType][0]
        return AddEventErrors.SUCCESS

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
        leafList = list(self.evaluatedLeaves) # Do a shallow copy
        root = self.root.copyNodes(None, leafList)
        return Tree(root, self.order, leafList, deepcopy(self.eventTypeToLeafDict), self.maxTimeDelta, self.minTime, self.maxTime, deepcopy(self.evaluationDictionary), self.leafIndex, self.isEmpty, list(self.evaluatedLeaves))
    
    @staticmethod
    def createLeftDeepTree(pattern: Pattern) -> Tree:
        order = OrderType.NOT_ORDERED if pattern.patternStructure.getTopOperator() == AndOperator else OrderType.ORDERED
        #Adding the sequences to the tree
        nodeList = []
        nodeCounter = 0
        eventTypeToLeafDict = {}
        for qItem in pattern.patternStructure.args:
            nodeList.append(TreeNode(qItem))
            if qItem.eventType not in eventTypeToLeafDict:
                eventTypeToLeafDict[qItem.eventType] = []
            eventTypeToLeafDict[qItem.eventType].append(nodeCounter)
            nodeCounter += 1
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
        return Tree(root, order, nodeList, eventTypeToLeafDict, pattern.slidingWindow)
    
    @staticmethod
    def __sequenceEval(pattern: Pattern, events: Stream, matches: Container, treeConstructionFunc):
        # Sort trees in dict based on their next incoming eventType
        treeDict = {}
        for qItem in pattern.patternStructure.args:
            treeDict[qItem.eventType] = []
        firstEventType = pattern.patternStructure.args[0].eventType
        treeDict[firstEventType].append(treeConstructionFunc(pattern))
        for event in events:
            currentEventType = event.eventType
            if currentEventType in treeDict: # Ignore events that or not in Sequence
                # Iterate backwards to enable element deletion while iterating
                for i in range(len(treeDict[currentEventType]) - 1, -1, -1):
                    copiedTree = []
                    currentTree = treeDict[currentEventType][i]
                    addEventStatus = currentTree.addEvent(event, copiedTree)
                    if (addEventStatus == AddEventErrors.NOT_WITHIN_TIMESCALE_ERROR):
                        del treeDict[currentEventType][i] # Will not be the empty tree
                    elif (addEventStatus == AddEventErrors.SUCCESS):
                        patternMatch = currentTree.getPatternMatch()
                        if (patternMatch != None):
                            matches.addItem(patternMatch)
                        else:
                            nextEventType = currentTree.getCurrentEventType()
                            treeDict[nextEventType].append(currentTree)
                        del treeDict[currentEventType][i]
                        treeDict[currentEventType].append(copiedTree[0]) # Add copy to end
        matches.close()
    
    @staticmethod
    def __conjunctionEval(pattern: Pattern, events: Stream, matches: Container, treeConstructionFunc):
        emptyTree = treeConstructionFunc(pattern)
        # Sort trees in dict based on their available event types
        treeDict = {}
        for qItem in pattern.patternStructure.args:
            if qItem.eventType not in treeDict:
                treeDict[qItem.eventType] = [emptyTree]
        for event in events:
            currentEventType = event.eventType
            if currentEventType in treeDict: # Ignore events that or not in Conjunction
                # Iterate backwards to enable element deletion while iterating
                for i in range(len(treeDict[currentEventType]) - 1, -1, -1):
                    copiedTree = []
                    currentTree = treeDict[currentEventType][i]
                    addEventStatus = currentTree.addEvent(event, copiedTree)
                    if (addEventStatus == AddEventErrors.NOT_WITHIN_TIMESCALE_ERROR):
                        del treeDict[currentEventType][i] # Will not be the empty tree
                    elif (addEventStatus == AddEventErrors.SUCCESS):
                        patternMatch = currentTree.getPatternMatch()
                        if (patternMatch != None):
                            matches.addItem(patternMatch)
                        if (len(currentTree.eventTypeToLeafDict[currentEventType]) == 0):
                            del treeDict[currentEventType][i]
                        # Add the copy tree to treeDict
                        eventTypeToLeafDict = copiedTree[0].eventTypeToLeafDict
                        for eventType in eventTypeToLeafDict:
                            if (len(eventTypeToLeafDict[eventType]) > 0):
                                treeDict[eventType].append(copiedTree[0])
        matches.close()

    @staticmethod
    def eval(pattern: Pattern, events: Stream, matches: Container, treeConstructionFunc = lambda pattern: Tree.createLeftDeepTree(pattern)):
        # Sequence Order
        if (pattern.patternStructure.getTopOperator() == SeqOperator):
            Tree.__sequenceEval(pattern, events, matches, treeConstructionFunc)    
        # Conjunction
        elif (pattern.patternStructure.getTopOperator() == AndOperator):
            Tree.__conjunctionEval(pattern, events, matches, treeConstructionFunc)

   
