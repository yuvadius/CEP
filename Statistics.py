from Formula import Formula
from Pattern import Pattern
from PatternStructure import SeqOperator, AndOperator, QItem
from IODataStructures import Stream

# Calculates the selectivity of a condition between two arguments, s.t. the formula of the condition between them is given.
def getConditionSelectivity(arg1 : QItem, arg2 : QItem, formula : Formula, stream : Stream, isSeq : bool):
    if not formula:
        return 1.0
    
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

# returns a dictionary: for each event type in the pattern, its number of occurences in stream.
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
            selMatrix[i][j] = selMatrix[j][i] = getConditionSelectivity(args[i], args[j], pattern.patternMatchingCondition.getFormulaOf({args[i].name, args[j].name}), stream.duplicate(), isSeq)

    return selMatrix

# Returns in arr(i) the arrival rate of event type i.
def getArrivalRates(pattern : Pattern, stream : Stream):
    timeIval = (stream.last().date - stream.first().date).total_seconds()
    typesCount = getOccurencesDict(pattern, stream.duplicate())
    args = pattern.patternStructure.args
    print(timeIval, typesCount)
    return [typesCount[i.eventType] / timeIval for i in args]

# Calculates the cost function of a given order.
def calculateOrderCostFunction(order, selectivityMatrix, arrivalRates, windowInSecs):
    cost = 0
    toAdd = 1
    for i in range(len(order)):
        toAdd *= selectivityMatrix[order[i]][order[i]] * arrivalRates[order[i]] * windowInSecs
        for j in range(i):
            toAdd *= selectivityMatrix[order[i]][order[j]]
        cost += toAdd
    return cost

def calculateTreeCostFunction(tree, selectivityMatrix, arrivalRates, windowInSecs):
    # use the helper function to calculate cost.
    _, _, cost = calculateTreeCostFunctionHelper(tree, selectivityMatrix, arrivalRates, windowInSecs)
    return cost

def calculateTreeCostFunctionHelper(tree, selectivityMatrix, arrivalRates, windowInSecs):
    # calculate base case: tree is a leaf.
    if type(tree) == int:
        cost = pm = windowInSecs * arrivalRates[tree] * selectivityMatrix[tree][tree]
        return [tree], pm, cost
    
    # calculate for left subtree
    leftArgs, leftPM, leftCost = calculateTreeCostFunctionHelper(tree[0], selectivityMatrix, arrivalRates, windowInSecs)
    # calculate for right subtree
    rightArgs, rightPM, rightCost = calculateTreeCostFunctionHelper(tree[1], selectivityMatrix, arrivalRates, windowInSecs)
    # calculate from left and right subtrees for this subtree.
    pm = leftPM * rightPM
    for l in leftArgs:
        for r in rightArgs:
            pm *= selectivityMatrix[l][r]
    cost = leftCost + rightCost + pm
    return leftArgs + rightArgs, pm, cost
