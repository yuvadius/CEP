
from __future__ import annotations
from datetime import datetime, timedelta
from Pattern import Pattern
from PatternStructure import *
from Formula import *
from IODataStructures import Container, Stream
from typing import List, Tuple
from Event import Event
from Utils import merge, mergeAccordingTo, isSorted
from PatternMatch import PatternMatch

class PartialMatch:
    def __init__(self, pm):
        self.pm = pm
        self.lastDate = max(pm, key=lambda x: x.date).date
        self.firstDate = min(pm, key=lambda x: x.date).date
    
    def getLastDate(self):
        return self.lastDate
    
    def getFirstDate(self):
        return self.firstDate
    
    def getPartialMatch(self):
        return self.pm

class Tree:
    def __init__(self, treeBluePrint, pattern : Pattern):
        self.isSeq = (pattern.patternStructure.getTopOperator() == SeqOperator)
        self.args = pattern.patternStructure.args
        self.window = pattern.slidingWindow
        self.formula = pattern.patternMatchingCondition
        self.root = Node.constructTree(self.isSeq, treeBluePrint, self.args, pattern.slidingWindow)
        self.leaves = self.root.getLeaves()
        self.applyFormula()
    
    def applyFormula(self):
        self.root.applyFormula(self.formula)

    def getLeaves(self):
        return self.leaves

    def getRootMatches(self):
        while self.root.partialMatches:
            ret = self.root.partialMatches[0].getPartialMatch()
            del self.root.partialMatches[0]
            yield ret
    
    def printReorder(self):
        self.root.printReorder()


class Node:
    def __init__(self, isSeq, slidingWindow, reorder : List[Tuple[int, QItem]] = None, parent = None, left = None, right = None):
        self.reorder = reorder
        self.parent = parent
        self.left = left
        self.right = right
        self.partialMatches = []
        self.slidingWindow = slidingWindow
        self.condition = TrueFormula()
        self.isSeq = isSeq
    
    def printReorder(self):
        print(self.reorder)
        if self.left:
            print("left:")
            self.left.printReorder()
            print("right:")
            self.right.printReorder()
        

    def getLeaves(self):
        if self.isLeaf():
            return [self]
        
        return self.left.getLeaves() + self.right.getLeaves()

    def applyFormula(self, formula):
        names = {item[1].name for item in self.reorder}
        condition = formula.getFormulaOf(names)
        self.condition = condition if condition else TrueFormula()
        if not self.isLeaf():
            self.left.applyFormula(self.condition)
            self.right.applyFormula(self.condition)
    

    def isLeaf(self):
        return self.left == self.right == None
    
    def getEventType(self):
        if not self.isLeaf():
            raise Exception()

        return self.reorder[0][1].eventType
    
    def setSubtrees(self, left, right):
        self.left = left
        self.right = right
        self.reorder = merge(self.left.reorder, self.right.reorder, lambda x: x[0])
    
    def setParent(self, parent):
        self.parent = parent
            
    @staticmethod 
    def constructTree(isSeq, tree, args, slidingWindow, parent = None):
        if type(tree) == int:
            return Node(isSeq, slidingWindow, [(tree, args[tree])], parent)
        
        current = Node(isSeq, slidingWindow)
        leftTree, rightTree = tree
        left = Node.constructTree(isSeq, leftTree, args, slidingWindow, current)
        right = Node.constructTree(isSeq, rightTree, args, slidingWindow, current)
        current.setSubtrees(left, right)
        current.setParent(parent)

        return current
    
    def isLeftSubtree(self):
        if self.parent == None:
            raise Exception()

        return (self.parent.left is self)
    
    def handleEvent(self, event : Event):
        if not self.isLeaf():
            raise Exception()

        self.updatePartialMatchesToDate(event.date)

        qitem = self.reorder[0][1]
        binding = {qitem.name:event.event}
        
        if self.condition.eval(binding):
            self.partialMatches.append(PartialMatch([event]))
            if self.parent != None:
                self.parent.handleNewPartialMatch(self.isLeftSubtree())
        
    
    def updatePartialMatchesToDate(self, lastDate):
        count = 0
        for partialMatch in self.partialMatches:
            if partialMatch.getFirstDate() + self.slidingWindow < lastDate:
                count += 1
            else:
                break
        self.partialMatches = self.partialMatches[count:]

    def handleNewPartialMatch(self, originatorIsLeftSubtree):
        if self.isLeaf():
            raise Exception()
        
        if originatorIsLeftSubtree:
            newPartialMatch = self.left.partialMatches[-1]
            firstReorder = self.left.reorder
            self.right.updatePartialMatchesToDate(newPartialMatch.getLastDate())
            toCompare = self.right.partialMatches
            secondReorder = self.right.reorder
        else:
            newPartialMatch = self.right.partialMatches[-1]
            firstReorder = self.right.reorder
            self.left.updatePartialMatchesToDate(newPartialMatch.getLastDate())
            toCompare = self.left.partialMatches
            secondReorder = self.left.reorder
        
        self.updatePartialMatchesToDate(newPartialMatch.getLastDate())

        for partialMatch in toCompare:
            if partialMatch.getLastDate() - newPartialMatch.getFirstDate() > self.slidingWindow \
            or newPartialMatch.getLastDate() - partialMatch.getFirstDate() > self.slidingWindow:
                continue
            speculativePM = mergeAccordingTo(firstReorder, secondReorder, 
            newPartialMatch.getPartialMatch(), partialMatch.getPartialMatch(), 
            lambda x: x[0])
            if self.isSeq and not isSorted(speculativePM, key=lambda x: x.counter):
                continue

            binding = {
                self.reorder[i][1].name : speculativePM[i].event 
                for i in range(len(self.reorder))
            }
            if self.condition.eval(binding):
                self.partialMatches.append(PartialMatch(speculativePM))
                if self.parent:
                    self.parent.handleNewPartialMatch(self.isLeftSubtree())
        return
        


class TreeAlgorithm:
    def eval(self, treeBluePrint, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        if elapsed:
            start = datetime.now()
        
        tree = Tree(treeBluePrint, pattern)
        eventTypesListeners = {}
        for leaf in tree.getLeaves():
            eventType = leaf.getEventType()
            if eventType in eventTypesListeners.keys():
                eventTypesListeners[eventType].append(leaf)
            else:
                eventTypesListeners[eventType] = [leaf]
        

        for event in events:
            if event.eventType in eventTypesListeners.keys():
                for leaf in eventTypesListeners[event.eventType]:
                    leaf.handleEvent(event)
                    for match in tree.getRootMatches():
                        matches.addItem(PatternMatch(match))
        
        matches.close()
        
        if elapsed:
            elapsed[0] = ((datetime.now() - start).total_seconds())
