from Formula import *
from Pattern import Pattern
from PatternStructure import SeqOperator, AndOperator, QItem
from IODataStructures import Stream
from IOUtils import *
from CEP import CEP
from Algorithms import TreeAlgorithm

def eventTypesCount(stream: Stream):
    ret = {}
    for event in stream:
        if event.eventType in ret.keys():
            ret[event.eventType] += 1
        else:
            ret[event.eventType] = 1
    return ret

def getConditionSelectivity(arg1 : QItem, arg2 : QItem, formula : Formula, stream : Stream, isSeq : bool):
    count = 0
    matchCount = 0
    
    if arg1 == arg2:
        for event in stream:
            if event.eventType == arg1.eventType:
                count += 1
                if formula.eval({arg1.name:event.event}):
                    matchCount += 1
    else:
        events1 = []
        events2 = []
        for event in stream:
            if event.eventType == arg1.eventType:
                events1.append(event)
            elif event.eventType == arg2.eventType:
                events2.append(event)
        for event1 in events1:
            for event2 in events2:
                if ((not isSeq) or event1.date < event2.date):
                    count += 1
                    if formula.eval({arg1.name:event1.event, arg2.name:event2.event}):
                        matchCount += 1
    return matchCount / count


def getOccurencesDict(pattern : Pattern, stream : Stream):
    ret = {}
    types = {qitem.eventType for qitem in pattern.patternStructure.args }
    for event in stream:
        if event.eventType in types:
            if event.eventType in ret.keys():
                ret[event.eventType] += 1
            else:
                ret[event.eventType] = 1
    return ret

# Return in sel(i,j) the selectivity of condition(i,j).
def getSelectivityMatrix(pattern : Pattern, stream : Stream):
    isSeq = (pattern.patternStructure.getTopOperator() == SeqOperator)
    
    args = pattern.patternStructure.args
    argsNum = len(args)
    selMatrix = [[0 for _ in range(argsNum)] for _ in range(argsNum)]
    for i in range(argsNum):
        for j in range(i + 1):
            selMatrix[i][j] = selMatrix[j][i] = getConditionSelectivity(args[i], args[j], pattern.patternMatchingCondition, stream.duplicate(), isSeq)

    return selMatrix

# Returns in arr(i) the arrival rate of event type i.
def getArrivalRates(pattern : Pattern, stream : Stream):
    timeIval = (stream.last().date - stream.first().date).total_seconds()
    typesCount = getOccurencesDict(pattern, stream.duplicate())
    args = pattern.patternStructure.args
    print(timeIval, typesCount)
    return [typesCount[i.eventType] / timeIval for i in args]


def calculateCostFunction(order, selectivityMatrix, arrivalRates, windowInSecs):
    cost = 0
    toAdd = 1
    for i in range(len(order)):
        toAdd *= selectivityMatrix[order[i]][order[i]] * arrivalRates[order[i]] * windowInSecs
        for j in range(i):
            toAdd *= selectivityMatrix[order[i]][order[j]]
        cost += toAdd
    return cost