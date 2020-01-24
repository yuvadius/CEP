from __future__ import annotations
from typing import List
from TreeBasedEvaluation import TreeAlgorithm
from IODataStructures import Stream, Container
from Pattern import Pattern
from Utils import MissingStatisticsException, buildTreeFromOrder, getOrderByOccurences, IterativeImprovementType, \
    swapGenerator, swapper, circleGenerator, circler, reverseCircle, getRandomOrder, StatisticsTypes
from Statistics import calculateOrderCostFunction

class OrderBasedAlgorithm(TreeAlgorithm):
    def eval(self, order: List[int], pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        tree = buildTreeFromOrder(order)
        super().eval(pattern, events, matches, tree, elapsed)

class TrivialAlgorithm(OrderBasedAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        argsNum = len(pattern.patternStructure.args)
        order = range(argsNum)
        super().eval(order, pattern, events, matches, elapsed)

class AscendingFrequencyAlgorithm(OrderBasedAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        frequencyDict = None
        if pattern.statisticsType == StatisticsTypes.FREQUENCY_DICT:
            frequencyDict = pattern.statistics
        else:
            raise MissingStatisticsException()
        order = getOrderByOccurences(pattern.patternStructure.args, frequencyDict)
        super().eval(order, pattern, events, matches, elapsed)
    

class GreedyAlgorithm(OrderBasedAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        order = GreedyAlgorithm.performGreedyOrder(selectivityMatrix, arrivalRates)
        super().eval(order, pattern, events, matches, elapsed)

    @staticmethod
    def performGreedyOrder(selectivityMatrix, arrivalRates):
        """
        At any step we will only consider the intermediate partial matches size,
        even without considering the sliding window.
        For each unselected item, we will calculate the speculated
        effect to the partial matches, and choose the one with minimal increase.
        """
        size = len(selectivityMatrix)
        if size == 1:
            return [0]
        
        newOrder = []
        leftToAdd = set(range(len(selectivityMatrix)))
        while len(leftToAdd) > 0:
            toAdd = toAddStart = leftToAdd.pop()
            minChangeFactor = selectivityMatrix[toAdd][toAdd]
            for j in newOrder:
                minChangeFactor *= selectivityMatrix[toAdd][j]
            
            for i in leftToAdd:
                changeFactor = selectivityMatrix[i][i] * arrivalRates[i]
                for j in newOrder:
                    changeFactor *= selectivityMatrix[i][j]
                if changeFactor < minChangeFactor:
                    minChangeFactor = changeFactor
                    toAdd = i
            newOrder.append(toAdd)
            
            if toAdd != toAddStart:
                leftToAdd.remove(toAdd)
                leftToAdd.add(toAddStart)
        
        return newOrder

class IterativeImprovement:
    def __init__(self, iiType : IterativeImprovementType = IterativeImprovementType.SWAP_BASED):
        self.iiType = iiType
    
    def iterativeImprovement(self, order, selectivityMatrix, arrivalRates, windowInSecs):
        if self.iiType == IterativeImprovementType.SWAP_BASED:
            movementGenerator = swapGenerator
            movementFunction = swapper
            reverseMove = lambda x: x
        else:
            movementGenerator = circleGenerator
            movementFunction = circler
            reverseMove = reverseCircle
        
        newOrder = order.copy()
        currCost = calculateOrderCostFunction(newOrder, selectivityMatrix, arrivalRates, windowInSecs)
        didSwap = True
        while didSwap:
            didSwap = False  # speculative
            for move in movementGenerator(len(newOrder)):
                movementFunction(newOrder, move)
                speculativeCost = calculateOrderCostFunction(newOrder, selectivityMatrix, arrivalRates, windowInSecs)
                if speculativeCost < currCost:
                    currCost = speculativeCost
                    didSwap = True
                    break
                else:
                    movementFunction(newOrder, reverseMove(move))
        return newOrder

class IIGreedyAlgorithm(IterativeImprovement, OrderBasedAlgorithm):
    def __init__(self, iiType : IterativeImprovementType = IterativeImprovementType.SWAP_BASED):
        super().__init__(iiType)
    
    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        order = GreedyAlgorithm.performGreedyOrder(selectivityMatrix, arrivalRates)
        order = self.iterativeImprovement(order, selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(order, pattern, events, matches, elapsed)

class IIRandomAlgorithm(IterativeImprovement, OrderBasedAlgorithm):
    def __init__(self, iiType : IterativeImprovementType = IterativeImprovementType.SWAP_BASED):
        super().__init__(iiType)

    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        order = getRandomOrder(len(arrivalRates))
        order = self.iterativeImprovement(order, selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(order, pattern, events, matches, elapsed)

class DynamicProgrammingLeftDeepAlgorithm(OrderBasedAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        order = DynamicProgrammingLeftDeepAlgorithm.findOrder(selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(order, pattern, events, matches, elapsed)
    
    @staticmethod
    def findOrder(selectivityMatrix, arrivalRates, window):
        # Save subsets' optimal orders, the cost and the left to add items.
        argsNum = len(selectivityMatrix)
        if argsNum == 1:  # boring extreme case
            return [0]
        
        items = frozenset(range(argsNum))
        subOrders = {frozenset({i}):([i], 
                        calculateOrderCostFunction([i], selectivityMatrix, arrivalRates, window), 
                        items.difference({i})) 
                        for i in items}
        
        for i in range(2, argsNum + 1):
            # for each subset of size i, we will find the best order for each subset
            nextOrders = {}
            for subset in subOrders.keys():
                order, _, leftToAdd = subOrders[subset]
                for item in leftToAdd:
                    # calculate for optional order for set of size i
                    newSubset = frozenset(subset.union({item}))
                    newCost = calculateOrderCostFunction(order, selectivityMatrix, arrivalRates, window)
                    # check if it is the current best order for that set
                    if newSubset in nextOrders.keys():
                        _, tCost, tLeft = nextOrders[newSubset]
                        if newCost < tCost:
                            newOrder = order + [item]
                            nextOrders[newSubset] = newOrder, newCost, tLeft
                    else:
                        newOrder = order + [item]
                        nextOrders[newSubset] = newOrder, newCost, leftToAdd.difference({item})
            # update subsets for next iteration    
            subOrders = nextOrders
        return list(subOrders.values())[0][0]