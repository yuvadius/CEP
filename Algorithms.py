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
    def __init__(self, valueType: QItem, value: Event = None, left: TreeNode = None, right: TreeNode = None, parent: TreeNode = None, formula: Formula = None, nodeBufferStorerIndex: int = None, nodeBeforeIndex: int = None, nodeAfterIndex: int = None):
        self.valueType = valueType
        self.value = value
        self.left = left
        self.right = right
        self.parent = parent
        self.formula = formula
        self.evaluation = False
        # Extra Information for input buffers
        self.nodeBufferStorerIndex = nodeBufferStorerIndex
        self.nodeBeforeIndex = nodeBeforeIndex
        self.nodeAfterIndex = nodeAfterIndex

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

    #Copy all nodes that are not yet evaluated from top to bottom
    def copyNodes(self, parentNode: TreeNode, leafList: List[TreeNode]) -> TreeNode:
        if (self.evaluation):
            return self
        left = None if self.left == None else self.left.copyNodes(self, leafList)
        right = None if self.right == None else self.right.copyNodes(self, leafList)
        node = TreeNode(self.valueType, self.value, None, None, None, self.formula, self.nodeBufferStorerIndex, self.nodeBeforeIndex, self.nodeAfterIndex)
        node.addNodes(left, right)
        if (left == None and right == None):
            leafList.append(node)
        return node

    #Evalute node from bottom to top recursively
    def __recursiveEvaluation(self, evalDictionary: Dict, nodesToEvaluate: List[TreeNode], previousEvaluatedNode: TreeNode = None):
        if self.evaluation == True:
            return True if self.parent == None else self.parent.__recursiveEvaluation(evalDictionary, nodesToEvaluate)
        #If sons evaluated to true
        elif (self.left == None or self.left.evaluation or self.left is previousEvaluatedNode) and (self.right == None or self.right.evaluation or self.right is previousEvaluatedNode):
            evaluation = True if (self.formula == None) else self.formula.eval(evalDictionary)
            if (evaluation == False):
                return False
            else:
                nodesToEvaluate.append(self)
            if (self.parent == None):#At top
                return True
            return self.parent.__recursiveEvaluation(evalDictionary, nodesToEvaluate, self)
        else:
            return True

    #Evalute node from bottom to top recursively
    def recursiveEvaluation(self, evalDictionary: Dict, nodesToEvaluate: List[TreeNode], currentLeaf: TreeNode, event: Event):
        evalDictionary[currentLeaf.valueType.name] = event.event # Tree change, make sure to delete before copy or failure(More efficient than a deep copy)
        returnValue = self.__recursiveEvaluation(evalDictionary, nodesToEvaluate)
        del evalDictionary[currentLeaf.valueType.name] # Undo tree change
        return returnValue

class Tree:
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

    def getCurrentLeaf(self, event: Event = None) -> TreeNode:
        if(self.order == OrderType.ORDERED or self.order == OrderType.LAZY_ORDERED):
            return self.leafList[self.leafIndex]
        elif(self.order == OrderType.NOT_ORDERED):
            return self.leafList[self.eventTypeToLeafDict[event.eventType][0]]
        else:
            return None

    #Add event to the tree, will return AddEventErrors.SUCCESS on success
    #and a copy of all the trees that should be sent back for evaluation
    def addEvent(self, event: Event, inputBuffer: Dict = None):
        treeCopies = []
        nodesToEvaluate = []
        currentLeaf = self.getCurrentLeaf(event)
        minTime, maxTime = self.getMinMaxTime(event)
        # Check with multiple tests that we can add the event
        addEventStatus = self.checkTests(event, minTime, maxTime, currentLeaf, nodesToEvaluate)
        if addEventStatus == AddEventErrors.SUCCESS: # Passed all tests!!! Now we can update the tree
            self.updateTree(event, minTime, maxTime, currentLeaf, nodesToEvaluate, treeCopies, inputBuffer)
        return addEventStatus, treeCopies

    def getMinMaxTime(self, event: Event):
        minTime = event.date if (self.minTime == None) else min(self.minTime, event.date)
        maxTime = event.date if (self.maxTime == None) else max(self.maxTime, event.date)
        return minTime, maxTime

    # Check if node is before the "before node" or equal in time
    def checkIfNodeBefore(self, event: Event, currentLeaf: TreeNode):
        if currentLeaf.nodeBufferStorerIndex != None and currentLeaf.nodeBeforeIndex != None:
            beforeNodeEvent = self.leafList[currentLeaf.nodeBeforeIndex].value
            if beforeNodeEvent != None and (event.date < beforeNodeEvent.date or (event.date == beforeNodeEvent.date and event.counter <= beforeNodeEvent.counter)):
                return True
        return False

    # Check if node is after the "after node" or equal in time
    def checkIfNodeAfter(self, event: Event, currentLeaf: TreeNode):
        if currentLeaf.nodeBufferStorerIndex != None and currentLeaf.nodeAfterIndex != None:
            afterNodeEvent = self.leafList[currentLeaf.nodeAfterIndex].value
            if afterNodeEvent != None and (event.date > afterNodeEvent.date or (event.date == afterNodeEvent.date and event.counter >= afterNodeEvent.counter)):
                return True
        return False

    def checkTests(self, event: Event, minTime: datetime, maxTime: datetime, currentLeaf: TreeNode, nodesToEvaluate: List[TreeNode]):
        # First to checks are input buffer checks
        if(self.checkIfNodeAfter(event, currentLeaf)):
            return AddEventErrors.LAZY_AFTER_RIGHT_NODE
        if(self.checkIfNodeBefore(event, currentLeaf)):
            return AddEventErrors.LAZY_BEFORE_LEFT_NODE
        if(self.maxTimeDelta != timedelta.max and minTime + self.maxTimeDelta < maxTime):
            return AddEventErrors.NOT_WITHIN_TIMESCALE_ERROR
        if(currentLeaf.valueType.eventType != event.eventType):
            return AddEventErrors.WRONG_EVENT_TYPE_ERROR
        if(currentLeaf.recursiveEvaluation(self.evaluationDictionary, nodesToEvaluate, currentLeaf, event) == False):
            return AddEventErrors.EVALUATION_ERROR
        return AddEventErrors.SUCCESS

    def updateTree(self, event: Event, minTime: datetime, maxTime: datetime, currentLeaf: TreeNode, nodesToEvaluate: List[TreeNode], treeCopies: List[Tree], inputBuffer: Dict):
        treeCopies.append(self.copy()) # Append original of the tree before any changes
        for node in nodesToEvaluate:
            node.evaluation = True
        self.evaluationDictionary[currentLeaf.valueType.name] = event.event
        self.minTime = minTime
        self.maxTime = maxTime
        self.leafIndex += 1
        self.evaluatedLeaves.append(currentLeaf)
        self.isEmpty = False
        currentLeaf.value = event
        del self.eventTypeToLeafDict[event.eventType][0]
        if(self.isTreeFull() == False):
            self.updateBufferNodes(inputBuffer, treeCopies)

    def updateBufferNodes(self, inputBuffer: Dict, treeCopies: List[Tree]):
        baseTree = self
        if(baseTree.order == OrderType.LAZY_ORDERED):
            currentLeaf = baseTree.getCurrentLeaf()
            if(currentLeaf.nodeBufferStorerIndex != None):
                buffer = inputBuffer[currentLeaf.valueType.eventType]
                if self.maxTimeDelta != timedelta.max:
                    minDate = None
                    if currentLeaf.nodeBeforeIndex != None and self.leafIndex > currentLeaf.nodeBeforeIndex:
                        minDate = baseTree.leafList[currentLeaf.nodeBeforeIndex].value.date
                    else:
                        minDate = baseTree.leafList[currentLeaf.nodeBufferStorerIndex].value.date - self.maxTimeDelta
                    dateSearch = binarySearchClosestEvent(inputBuffer[currentLeaf.valueType.eventType], minDate)
                    buffer = buffer[dateSearch:]
                baseTreeIndex = len(treeCopies) # Where will the base tree be
                for event in buffer:
                    nodesToEvaluate = []
                    minTime, maxTime = baseTree.getMinMaxTime(event)
                    addEventStatus = baseTree.checkTests(event, minTime, maxTime, currentLeaf, nodesToEvaluate)
                    if addEventStatus == AddEventErrors.SUCCESS: # Passed all tests!!! Now we can update the tree
                        baseTree.updateTree(event, minTime, maxTime, currentLeaf, nodesToEvaluate, treeCopies, inputBuffer)
                        baseTree = treeCopies[baseTreeIndex]
                        baseTreeIndex = len(treeCopies)
                        currentLeaf = baseTree.getCurrentLeaf()
                    elif addEventStatus == AddEventErrors.LAZY_AFTER_RIGHT_NODE:
                        break

    def isTreeFull(self) -> bool:
        return self.root.evaluation

    def getPatternMatch(self) -> PatternMatch:
        if (self.root.evaluation == False):
            return None
        events = []
        if (self.order != OrderType.LAZY_ORDERED):
            for node in self.leafList:
                events.append(node.value)
            return PatternMatch(events)
        else:
            for node in self.leafList:
                if node.nodeBeforeIndex == None:
                    for _ in self.leafList:
                        events.append(node.value)
                        if node.nodeAfterIndex != None:
                            node = self.leafList[node.nodeAfterIndex]
                        else:
                           return PatternMatch(events)

    def getCurrentEventType(self) -> str:
        return self.leafList[self.leafIndex].valueType.eventType

    def copy(self) -> Tree:
        leafList = list(self.evaluatedLeaves) # Do a shallow copy
        root = self.root.copyNodes(None, leafList)
        return Tree(root, self.order, leafList, deepcopy(self.eventTypeToLeafDict), self.maxTimeDelta, self.minTime, self.maxTime, deepcopy(self.evaluationDictionary), self.leafIndex, self.isEmpty, list(self.evaluatedLeaves))

    @staticmethod
    def createInputBuffer(tree: Tree) -> Dict:
        inputBuffer = {}
        for node in tree.leafList:
            if node.nodeBufferStorerIndex != None:
                inputBuffer[node.valueType.eventType] = []
        return inputBuffer

    # Update the nodes so that they will support input buffers
    @staticmethod
    def sortNodesByFrequency(pattern: Pattern, nodeList: List[TreeNode]):
        if pattern.frequency:
            # Save neighbors(Will update to indexes at end)
            for i in range(len(nodeList)):
                if i != 0: # If not first
                    nodeList[i].nodeBeforeIndex = nodeList[i - 1]
                if i != (len(nodeList) - 1): # If not last
                    nodeList[i].nodeAfterIndex = nodeList[i + 1]
            # Rearange nodes and add buffers to nodes
            for _ in nodeList:
                for i in range(len(nodeList) - 1):
                    if pattern.frequency[nodeList[i].valueType.eventType] > pattern.frequency[nodeList[i + 1].valueType.eventType]:
                        swap(nodeList, i, i + 1)
                        # Update buffers
                        if nodeList[i + 1].nodeBufferStorerIndex == None:
                            nodeList[i + 1].nodeBufferStorerIndex = i
            # Update redundant nodeBufferStorerIndex
            for _ in nodeList:
                for i in range(len(nodeList)):
                    if nodeList[i].nodeBufferStorerIndex != None:
                        if nodeList[nodeList[i].nodeBufferStorerIndex].nodeBufferStorerIndex != None:
                            nodeList[i].nodeBufferStorerIndex = nodeList[nodeList[i].nodeBufferStorerIndex].nodeBufferStorerIndex
            # Update to indexes
            for node in nodeList:
                for i in range(len(nodeList)):
                    if node.nodeBeforeIndex is nodeList[i]:
                        node.nodeBeforeIndex = i
                    elif node.nodeAfterIndex is nodeList[i]:
                        node.nodeAfterIndex = i

    @staticmethod
    def createLeftDeepTree(pattern: Pattern) -> Tree:
        order = OrderType.ORDERED 
        if pattern.patternStructure.getTopOperator() == AndOperator:
            order = OrderType.NOT_ORDERED
        elif pattern.frequency:
            order = OrderType.LAZY_ORDERED
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
        if pattern.frequency:
            Tree.sortNodesByFrequency(pattern, nodeList)
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

class TreeAlgorithm(Algorithm):
    def __init__(self):
        self.treeDict = None

    def __sequenceEval(self, pattern: Pattern, events: Stream, matches: Container, treeConstructionFunc):
        # Sort trees in dict based on their next incoming eventType
        self.treeDict = {}
        emptyTree = treeConstructionFunc(pattern)
        inputBuffer = Tree.createInputBuffer(emptyTree)
        for node in emptyTree.leafList:
            if node.nodeBufferStorerIndex == None: # If node doesn't use the buffer
                self.treeDict[node.valueType.eventType] = []
        firstEventType = emptyTree.leafList[0].valueType.eventType
        self.treeDict[firstEventType].append(treeConstructionFunc(pattern))
        for event in events:
            currentEventType = event.eventType
            if currentEventType in inputBuffer: # Insert event into input buffer
                inputBuffer[currentEventType].append(event)
            if currentEventType in self.treeDict: # Ignore events that are not in Sequence
                # Iterate backwards to enable element deletion while iterating
                for i in range(len(self.treeDict[currentEventType]) - 1, -1, -1):
                    currentTree = self.treeDict[currentEventType][i]
                    addEventStatus, copiedTrees = currentTree.addEvent(event, inputBuffer)
                    copiedTrees.append(currentTree)
                    if (addEventStatus == AddEventErrors.NOT_WITHIN_TIMESCALE_ERROR):
                        del self.treeDict[currentEventType][i] # Will not be the empty tree
                    elif (addEventStatus == AddEventErrors.SUCCESS):
                        del self.treeDict[currentEventType][i] # Delete current tree location
                        for tree in copiedTrees:
                            patternMatch = tree.getPatternMatch()
                            if (patternMatch != None):
                                matches.addItem(patternMatch)
                            elif tree.getCurrentLeaf().nodeBufferStorerIndex == None: # Make sure it's not a buffer node
                                nextEventType = tree.getCurrentEventType()
                                self.treeDict[nextEventType].append(tree) # We add current tree to search for next event type
        matches.close()
    
    def __conjunctionEval(self, pattern: Pattern, events: Stream, matches: Container, treeConstructionFunc):
        emptyTree = treeConstructionFunc(pattern)
        # Sort trees in dict based on their available event types
        self.treeDict = {}
        for qItem in pattern.patternStructure.args:
            if qItem.eventType not in self.treeDict:
                self.treeDict[qItem.eventType] = [emptyTree]
        for event in events:
            currentEventType = event.eventType
            if currentEventType in self.treeDict: # Ignore events that or not in Conjunction
                # Iterate backwards to enable element deletion while iterating
                for i in range(len(self.treeDict[currentEventType]) - 1, -1, -1):
                    currentTree = self.treeDict[currentEventType][i]
                    addEventStatus, copiedTrees = currentTree.addEvent(event)
                    copiedTrees.append(currentTree)
                    if (addEventStatus == AddEventErrors.NOT_WITHIN_TIMESCALE_ERROR):
                        del self.treeDict[currentEventType][i] # Will not be the empty tree, because we can always add to it.
                    elif (addEventStatus == AddEventErrors.SUCCESS):
                        patternMatch = currentTree.getPatternMatch()
                        if (patternMatch != None):
                            matches.addItem(patternMatch)
                        if (len(currentTree.eventTypeToLeafDict[currentEventType]) == 0):
                            del self.treeDict[currentEventType][i]
                        # Add the copy tree to treeDict
                        for tree in copiedTrees:
                            if not (tree is currentTree):
                                eventTypeToLeafDict = copiedTrees[0].eventTypeToLeafDict
                                for eventType in eventTypeToLeafDict:
                                    if (len(eventTypeToLeafDict[eventType]) > 0):
                                        self.treeDict[eventType].append(copiedTrees[0])
        matches.close()

    def eval(self, pattern: Pattern, events: Stream, matches: Container, treeConstructionFunc = lambda pattern: Tree.createLeftDeepTree(pattern)):
        # Sequence Order
        if (pattern.patternStructure.getTopOperator() == SeqOperator):
            self.__sequenceEval(pattern, events, matches, treeConstructionFunc)    
        # Conjunction
        elif (pattern.patternStructure.getTopOperator() == AndOperator):
            self.__conjunctionEval(pattern, events, matches, treeConstructionFunc)

   
