from abc import ABC
from Pattern import Pattern
from IODataStructures import Stream, Container

'''
Every evaluation mechanism shall inherit from the evaluation mechanism class and implement the
eval function which is used for evaluation. The evaluation mechanism may extend eval's signature if
the evaluation depends on more parameters, but shall include all presented parameters.
Contravariance of paramter types is allowed.
'''

class EvaluationMechanism(ABC):
    def eval(self, pattern: Pattern, events: Stream, matches: Container):
        pass

    def isMultiplePatternCompatible(self):
        pass