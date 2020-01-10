from Algorithms import TreeAlgorithm
from IODataStructures import Stream, Container
from Pattern import *
from Utils import StatisticsTypes, getOrderByOccurences
from Statistics import getSelectivityMatrix, getArrivalRates, getOccurencesDict
from IOUtils import fileInput


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