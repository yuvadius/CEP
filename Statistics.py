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

def getConditionOccurenceCount(arg1 : QItem, arg2 : QItem, formula : Formula, stream : Stream):
    pattern = Pattern(SeqOperator([arg1, arg2]), formula)
    output = Stream()
    cep = CEP(TreeAlgorithm(), [pattern], stream, output)
    count = 0
    for _ in output:
        count += 1
    return count

def getUnaryConditionOccurenceCount(arg : QItem, formula : Formula, stream : Stream):
    pattern = Pattern(SeqOperator([arg]), formula)
    output = Stream()
    cep = CEP(TreeAlgorithm(), [pattern], stream, output)
    count = 0
    for _ in output:
        count += 1
    return count


def getOccurencesDict(pattern : Pattern, stream : Stream):
    ret = {}
    types = {qitem.eventType for qitem in pattern.patternStructure.args }
    for event in stream:
        if event.eventType in ret.keys() and event.eventType in types:
            ret[event.eventType] += 1
        else:
            ret[event.eventType] = 1
    return ret

# Return in sel(i,j) the selectivity of condition(i,j).
def getSelectivityMatrix(pattern : Pattern, stream : Stream):
    if pattern.patternStructure.getTopOperator() != SeqOperator:
        return
    
    typesCount = getOccurencesDict(pattern, stream.duplicate())
    args = pattern.patternStructure.args
    argsNum = len(args)
    selMatrix = [[0 for _ in range(argsNum)] for _ in range(argsNum)]
    for i in range(argsNum):
        selMatrix[i][i] = typesCount[args[i].eventType]
        for j in range(i):
            selMatrix[i][j] = selMatrix[j][i] = getConditionOccurenceCount(args[i], args[j], pattern.patternMatchingCondition, stream.duplicate()) / getConditionOccurenceCount(args[i], args[j], TrueFormula(), stream.duplicate())
    for i in range(argsNum):
        selMatrix[i][i] = getUnaryConditionOccurenceCount(args[i], pattern.patternMatchingCondition, stream.duplicate()) / typesCount[args[i].eventType]
    return selMatrix

# Returns in arr(i) the arrival rate of event type i.
def getArrivalRates(pattern : Pattern, stream : Stream):
    timeIval = (stream.last().date - stream.first().date).total_seconds()
    typesCount = getOccurencesDict(pattern, stream.duplicate())
    args = pattern.patternStructure.args
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

events = fileInput("NASDAQ_20080201_1_sorted.txt", 
    [
        "Stock Ticker", 
        "Date", 
        "Opening Price", 
        "Peak Price", 
        "Lowest Price", 
        "Close Price", 
        "Volume"],
    "Stock Ticker",
    "Date")

pattern = Pattern(
    SeqOperator([QItem("MSFT", "a"), QItem("DRIV", "b"), QItem("ORLY", "c"), QItem("CBRL", "d")]),
    AndFormula(
        AndFormula(
            SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
            SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"]))
        ),
        SmallerThanFormula(IdentifierTerm("c", lambda x: x["Peak Price"]), IdentifierTerm("d", lambda x: x["Peak Price"]))
    ),
    timedelta(minutes=3)
)