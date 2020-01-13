from Algorithms import TreeAlgorithm
from IODataStructures import Stream, Container
from Pattern import *
from Utils import *
from Statistics import *

class TrivialAlgorithm(TreeAlgorithm):
    pass

class AscendingFrequencyAlgorithm(TreeAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        frequencyDict = None
        if pattern.statisticsType == StatisticsTypes.FREQUENCY_DICT:
            frequencyDict = pattern.statistics
        else:
            frequencyDict = getOccurencesDict(pattern, events.duplicate())
        pattern.newOrder = getOrderByOccurences(pattern.patternStructure.args, frequencyDict)
        super().eval(pattern, events, matches, elapsed)
    

class GreedyAlgorithm(TreeAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            selectivityMatrix = getSelectivityMatrix(pattern, events)
            arrivalRates = getArrivalRates(pattern, events)
        pattern.newOrder = GreedyAlgorithm.performGreedyOrder(selectivityMatrix, arrivalRates)
        super().eval(pattern, events, matches, elapsed)

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

class IIGreedyAlgorithm(IterativeImprovement, GreedyAlgorithm):
    def __init__(self, iiType : IterativeImprovementType = IterativeImprovementType.SWAP_BASED):
        super().__init__(iiType)
    
    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            selectivityMatrix = getSelectivityMatrix(pattern, events)
            arrivalRates = getArrivalRates(pattern, events)
        pattern.newOrder = IIGreedyAlgorithm.performGreedyOrder(selectivityMatrix, arrivalRates)
        pattern.newOrder = self.iterativeImprovement(pattern.newOrder, selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(pattern, events, matches, elapsed)

class IIRandomAlgorithm(IterativeImprovement, TreeAlgorithm):
    def __init__(self, iiType : IterativeImprovementType = IterativeImprovementType.SWAP_BASED):
        super().__init__(iiType)

    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            selectivityMatrix = getSelectivityMatrix(pattern, events)
            arrivalRates = getArrivalRates(pattern, events)
        pattern.newOrder = getRandomOrder(len(arrivalRates))
        pattern.newOrder = self.iterativeImprovement(pattern.newOrder, selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(pattern, events, matches, elapsed)

class DynamicProgrammingLeftDeepAlgorithm(TreeAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, elapsed = None):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            selectivityMatrix = getSelectivityMatrix(pattern, events)
            arrivalRates = getArrivalRates(pattern, events)
        pattern.newOrder = DynamicProgrammingLeftDeepAlgorithm.findOrder(selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(pattern, events, matches, elapsed)
    
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