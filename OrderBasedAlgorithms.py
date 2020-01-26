from __future__ import annotations
from typing import List
from TreeBasedEvaluation import TreeAlgorithm
from IODataStructures import Stream, Container
from Pattern import Pattern
from Utils import MissingStatisticsException, buildTreeFromOrder, getOrderByOccurences, IterativeImprovementType, \
    swapGenerator, swapper, circleGenerator, circler, reverseCircle, getRandomOrder, StatisticsTypes
from Statistics import calculateOrderCostFunction

class OrderBasedAlgorithm(TreeAlgorithm):
    def eval(self, order: List[int], pattern: Pattern, events: Stream, matches: Container, measureTime=False):
        tree = buildTreeFromOrder(order)
        super().eval(pattern, events, matches, tree, measureTime)

class TrivialAlgorithm(OrderBasedAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, measureTime=False):
        argsNum = len(pattern.patternStructure.args)
        order = list(range(argsNum)) # Trivial order.
        super().eval(order, pattern, events, matches, measureTime)

class AscendingFrequencyAlgorithm(OrderBasedAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, measureTime=False):
        frequencyDict = None
        if pattern.statisticsType == StatisticsTypes.FREQUENCY_DICT:
            frequencyDict = pattern.statistics
            order = getOrderByOccurences(pattern.patternStructure.args, frequencyDict)
        elif pattern.statisticsType == StatisticsTypes.ARRIVAL_RATES:
            arrivalRates = pattern.statistics
            # create an index-arrival rate binding and sort according to arrival rate.
            sortedOrder = sorted([(i, arrivalRates[i]) for i in range(len(arrivalRates))], key=lambda x:x[1])
            order = [x for x,y in sortedOrder] # create order from sorted binding.
        else:
            raise MissingStatisticsException()
        super().eval(order, pattern, events, matches, measureTime)
    

class GreedyAlgorithm(OrderBasedAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, measureTime=False):
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        order = GreedyAlgorithm.performGreedyOrder(selectivityMatrix, arrivalRates)
        super().eval(order, pattern, events, matches, measureTime)

    @staticmethod
    def performGreedyOrder(selectivityMatrix, arrivalRates):
        """
        At any step we will only consider the intermediate partial matches size,
        even without considering the sliding window, because the result is independent of it.
        For each unselected item, we will calculate the speculated
        effect to the partial matches, and choose the one with minimal increase.
        We don't even need to calculate the cost function. 
        """
        size = len(selectivityMatrix)
        if size == 1:
            return [0]
        
        newOrder = []
        leftToAdd = set(range(len(selectivityMatrix)))
        while len(leftToAdd) > 0:
            # create first nominee to add.
            toAdd = toAddStart = leftToAdd.pop()
            minChangeFactor = selectivityMatrix[toAdd][toAdd]
            for j in newOrder:
                minChangeFactor *= selectivityMatrix[toAdd][j]
            
            # find minimum change factor and its acorrding index.
            for i in leftToAdd:
                changeFactor = selectivityMatrix[i][i] * arrivalRates[i]
                for j in newOrder:
                    changeFactor *= selectivityMatrix[i][j]
                if changeFactor < minChangeFactor:
                    minChangeFactor = changeFactor
                    toAdd = i
            newOrder.append(toAdd)
            
            # if it wasn't the first nominee, then we need to fix the starting speculation we did.
            if toAdd != toAddStart:
                leftToAdd.remove(toAdd)
                leftToAdd.add(toAddStart)
        
        return newOrder

class IterativeImprovement:
    def __init__(self, iiType : IterativeImprovementType = IterativeImprovementType.SWAP_BASED):
        self.iiType = iiType
    
    def copy(self):
        return self.__class__(self.iiType)
    
    def iterativeImprovement(self, order, selectivityMatrix, arrivalRates, windowInSecs):
        # Choose the iteration functions according to iteration type.
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
        OrderBasedAlgorithm.__init__(self)
    
    def copy(self):
        return self.__class__(self.iiType)
    
    def eval(self, pattern: Pattern, events: Stream, matches: Container, measureTime=False):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        order = GreedyAlgorithm.performGreedyOrder(selectivityMatrix, arrivalRates)
        order = self.iterativeImprovement(order, selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(order, pattern, events, matches, measureTime)

class IIRandomAlgorithm(IterativeImprovement, OrderBasedAlgorithm):
    def __init__(self, iiType : IterativeImprovementType = IterativeImprovementType.SWAP_BASED):
        super().__init__(iiType)
        OrderBasedAlgorithm.__init__(self)
    
    def copy(self):
        return self.__class__(self.iiType)

    def eval(self, pattern: Pattern, events: Stream, matches: Container, measureTime=False):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        order = getRandomOrder(len(arrivalRates))
        order = self.iterativeImprovement(order, selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(order, pattern, events, matches, measureTime)

class DynamicProgrammingLeftDeepAlgorithm(OrderBasedAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, measureTime=False):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        order = DynamicProgrammingLeftDeepAlgorithm.findOrder(selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(order, pattern, events, matches, measureTime)
    
    @staticmethod
    def findOrder(selectivityMatrix, arrivalRates, window):
        argsNum = len(selectivityMatrix)
        if argsNum == 1:  # boring extreme case
            return [0]
        
        items = frozenset(range(argsNum))
        # Save subsets' optimal orders, the cost and the left to add items.
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
                    # check if it is not the first order for that set
                    if newSubset in nextOrders.keys():
                        _, tCost, tLeft = nextOrders[newSubset]
                        if newCost < tCost:  # check if it is the current best order for that set
                            newOrder = order + [item]
                            nextOrders[newSubset] = newOrder, newCost, tLeft
                    else: # if it is the first order for that set
                        newOrder = order + [item]
                        nextOrders[newSubset] = newOrder, newCost, leftToAdd.difference({item})
            # update subsets for next iteration
            subOrders = nextOrders
        return list(subOrders.values())[0][0]  # return the order (at index 0 in the tuple) of item 0, the only item in subsets of size n.