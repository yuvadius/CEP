from TreeBasedEvaluation import TreeAlgorithm
from IODataStructures import Stream, Container
from Pattern import Pattern
from Utils import StatisticsTypes, getAllDisjointSets, MissingStatisticsException
from Statistics import calculateTreeCostFunction
from OrderBasedAlgorithms import GreedyAlgorithm
from itertools import combinations

class DynamicProgrammingBushyAlgorithm(TreeAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, measureTime=False):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        tree = DynamicProgrammingBushyAlgorithm.findTree(selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(pattern, events, matches, tree, measureTime)
    
    @staticmethod
    def findTree(selectivityMatrix, arrivalRates, window):
        argsNum = len(selectivityMatrix)
        if argsNum == 1:
            return [0]
        
        items = frozenset(range(argsNum))
        # Save subsets' optimal topologies, the cost and the left to add items.
        subTrees = {frozenset({i}):(i, 
                        calculateTreeCostFunction(i, selectivityMatrix, arrivalRates, window), 
                        items.difference({i}))
                        for i in items}
        
        # for each subset of size i, find optimal topology for these subsets according to size (i-1) subsets.
        for i in range(2, argsNum + 1):
            for tSubset in combinations(items, i):
                subset = frozenset(tSubset)
                disjointSetsIter = getAllDisjointSets(subset) # iterator for all disjoint splits of a set.
                # use first option as speculative best.
                set1_, set2_ = next(disjointSetsIter)
                tree1_, _, _ = subTrees[set1_]
                tree2_, _, _ = subTrees[set2_]
                newTree_ = (tree1_, tree2_)
                newCost_ = calculateTreeCostFunction(newTree_, selectivityMatrix, arrivalRates, window)
                newLeft_ = items.difference({subset})
                subTrees[subset] = newTree_, newCost_, newLeft_
                # find the best topology based on previous topologies for smaller subsets.
                for set1, set2 in disjointSetsIter:
                    tree1, _, _ = subTrees[set1]
                    tree2, _, _ = subTrees[set2]
                    newTree = (tree1, tree2)
                    newCost = calculateTreeCostFunction(newTree, selectivityMatrix, arrivalRates, window)
                    _, cost, left = subTrees[subset]
                    # if new subset's topology is better, then update to it.
                    if newCost < cost:
                        subTrees[subset] = newTree, newCost, left
        return subTrees[items][0] # return the best topology (index 0 at tuple) for items - the set of all arguments.


class ZStreamAlgorithm(TreeAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, measureTime=False):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        tree = ZStreamAlgorithm.findTree(selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(pattern, events, matches, tree, measureTime)
    
    @staticmethod
    def findTree(selectivityMatrix, arrivalRates, window):
        order = list(range(len(selectivityMatrix)))
        return ZStreamAlgorithm.findTreeForOrder(order, selectivityMatrix, arrivalRates, window)
    
    @staticmethod
    def findTreeForOrder(order,selectivityMatrix, arrivalRates, window):
        argsNum = len(order)
        items = tuple(order)
        suborders = {
            (i,): (i, calculateTreeCostFunction(i, selectivityMatrix, arrivalRates, window))
            for i in items
        }

        # iterate over suborders' sizes
        for i in range(2, argsNum + 1):
            # iterate over suborders of size i
            for j in range(argsNum - i + 1):
                # create the suborder (slice) to find its optimum.
                suborder = tuple(order[t] for t in range(j, j + i))
                # use first split of suborder as speculative best.
                order1_, order2_ = suborder[:1], suborder[1:]
                tree1_, _ = suborders[order1_]
                tree2_, _ = suborders[order2_]
                tree = (tree1_, tree2_)
                cost = calculateTreeCostFunction(tree, selectivityMatrix, arrivalRates, window)
                suborders[suborder] = tree, cost
                # iterate over splits of suborder
                for k in range(2, i):
                    # find the optimal topology of this split, according to optimal topologies of subsplits.
                    order1, order2 = suborder[:k], suborder[k:]
                    tree1, _ = suborders[order1]
                    tree2, _ = suborders[order2]
                    _, prevCost = suborders[suborder]
                    newTree = (tree1, tree2)
                    newCost = calculateTreeCostFunction(newTree, selectivityMatrix, arrivalRates, window)
                    if newCost < prevCost:
                        suborders[suborder] = newTree, newCost
        return suborders[items][0] # return the topology (index 0 at tuple) of the entire order, indexed to 'items'.

class ZStreamOrdAlgorithm(TreeAlgorithm):
    def eval(self, pattern: Pattern, events: Stream, matches: Container, measureTime=False):
        selectivityMatrix = None
        if pattern.statisticsType == StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES:
            (selectivityMatrix, arrivalRates) = pattern.statistics
        else:
            raise MissingStatisticsException()
        order = GreedyAlgorithm.performGreedyOrder(selectivityMatrix, arrivalRates)
        tree = ZStreamAlgorithm.findTreeForOrder(order, selectivityMatrix, arrivalRates, pattern.slidingWindow.total_seconds())
        super().eval(pattern, events, matches, tree, measureTime)