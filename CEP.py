'''
This file contains the primary engine,
which invokes evaluations and manages streams.
It now is supporting multiple patterns in a very non-sophisticated way:
It just invokes the same algorithm multiple times in parallel. But in future versions,
there is an option to add a multiple patterns support in the algorithms. 
'''

import threading
from Event import Event
from PatternMatch import PatternMatch
from IODataStructures import Stream, Container
from Pattern import Pattern
from typing import List
from EvaluationMechanism import EvaluationMechanism

# A sketch of QoS specifications, we assume it will be an object constructed separately, and the
# CEP engine will refer to it if it is passed.
# Not implemented yet.
class PerformanceSpecifications:
    def __init__(self, memoryLimit, constructionTimeLimit, **kwargs):
        pass

class CEP:
    '''
    This class has an algorithm, an input stream and an output container.
    It also has several input patterns which can always be added after init, and some configuration parameters.
    '''
    def __init__(self, algorithm: EvaluationMechanism, patterns: List[Pattern] = None, events: Stream = None, 
        output: Container = None, saveReplica: bool = True, 
        performanceSpecs : PerformanceSpecifications = None):
        if algorithm.isMultiplePatternCompatible():
            raise NotImplementedError()
        # Otherwise, every pattern is handled separately.
        self.eventStreams = []
        self.patternMatches = output if output else Stream()
        self.algorithmObjects = {}
        self.algorithm = algorithm
        # base stream is the replica being saved
        if saveReplica and events:
            self.baseStream = events
        elif saveReplica:
            self.baseStream = Stream()
        else:
            self.baseStream = None
        
        # Initialize all given pattern evaluation.
        # For each pattern we send to the algorithm evaluation function the pattern, the input stream, the output stream,
        # and measureTime=True, in order to measure the time it took to evaluate it. We start the evaluation in
        # a new thread.
        if patterns:
            for pattern in patterns:
                eventStream = self.baseStream.duplicate() if self.baseStream else Stream()
                self.algorithmObjects[pattern] = algorithm.copy()
                worker = threading.Thread(target = self.algorithmObjects[pattern].eval, args = (pattern, eventStream, self.patternMatches, True))
                worker.start()
                self.eventStreams.append(eventStream)

    # This is a blocking function which will wait for the evaluation to finish and then return the
    # time it took to evalute the given pattern.
    def getElapsed(self, pattern):
        if pattern not in self.algorithmObjects.keys():
            raise Exception("Pattern is not evaluated")
        return self.algorithmObjects[pattern].getElapsed()

    # Add an event to the event stream. Useful for realtime events.
    # Since every pattern evaluation consumes events from a different stream,
    # we need to add the event to every stream.
    def addEvent(self, event: Event):
        for eventStream in self.eventStreams: 
            eventStream.addItem(event)
        if self.baseStream:
            self.baseStream.addItem(event)
    
    # Add a pattern to be evaluated by this CEP object.
    # we send to the algorithm evaluation function the pattern, the input stream, the output stream,
    # and measureTime=True, in order to measure the time it took to evaluate it. We start the evaluation in
    # a new thread.
    def addPattern(self, pattern: Pattern, priority: int = 0):
        if pattern in self.algorithmObjects.keys():
            return # pattern is already evaluated.
        eventStream = self.baseStream.duplicate() if self.baseStream else Stream()
        self.algorithmObjects[pattern] = self.algorithm.copy()
        worker = threading.Thread(target = self.algorithmObjects[pattern].eval, args = (pattern, eventStream, self.patternMatches))
        worker.start()
        self.eventStreams.append(eventStream)
    
    # return one match from the output container.
    def getPatternMatch(self):
        try:
            return self.patternMatches.getItem()
        except StopIteration: # the container might be closed.
            return None
    
    # return the output container itself.
    def getPatternMatchContainer(self):
        return self.patternMatches

    # close the input stream.
    def close(self):
        for eventStream in self.eventStreams:
            eventStream.close()
        if self.baseStream:
            self.baseStream.close()
