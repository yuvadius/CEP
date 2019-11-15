from abc import ABC  # Abstract Base Class

'''
This file contains many object definitions which aren't very informative as much as formal.
The mechanism is described easily with examples.

*** usage examples: ***
x = AndFormula(EqFormula(AtomicTerm(5), IdentifierTerm("Moti", lambda x: x["age"])), 
        SmallerThanEqFormula(AtomicTerm(13), MulTerm(AtomicTerm(5), AtomicTerm(3))))  # 5 == Moti["age"] and 13 <= 5 * 3
x.eval({ "Moti" : { "age": 5 } })  # True
x.eval({ "Moti" : { "age": 31 } })  # False
x.eval()

To do: Insert more examples

'''

class Term(ABC):
    '''
    Evaluates to the term's value. 
    If there are variables (identifiers) in the term, a name-value binding shall be inputted.
    '''
    def eval(self, binding: dict = {}):
        pass


class AtomicTerm(Term):
    def __init__(self, value):
        self.value = value
    
    def eval(self, binding: dict = {}):
        return self.value

        
class IdentifierTerm(Term):
    def __init__(self, name: str, getAttrFunc):
        self.name = name
        self.getAttrFunc = getAttrFunc
    
    def eval(self, binding: dict = {}):
        if not type(binding) == dict or not self.name in binding:
            raise NameError("Name %s is not bound to a value" % self.name)
        return self.getAttrFunc(binding[self.name])

        
class BinaryOperationTerm(Term):
    def __init__(self, lhs, rhs, binOp):
        self.lhs = lhs
        self.rhs = rhs
        self.binOp = binOp
    
    def eval(self, binding: dict = {}):
        return self.binOp(self.lhs.eval(binding), self.rhs.eval(binding))

        
class PlusTerm(BinaryOperationTerm):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs, lambda x, y: x + y)
        
class MinusTerm(BinaryOperationTerm):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs, lambda x, y: x - y)
        
class MulTerm(BinaryOperationTerm):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs, lambda x, y: x * y)

        
class DivTerm(BinaryOperationTerm):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs, lambda x, y: x / y)

        
class Formula(ABC):
    '''
    Returns whether the parameters satisfy the formula. It evaluates to True or False.
    If there are variables (identifiers) in the formula, a name-value binding shall be inputted.
    '''
    def eval(self, binding: dict = {}):
        pass

        
class AtomicFormula(Formula):
    def __init__(self, leftTerm, rightTerm, relBinOp):
        self.leftTerm = leftTerm
        self.rightTerm = rightTerm
        self.relBinOp = relBinOp
    
    def eval(self, binding: dict = {}):
        try:
            return self.relBinOp(self.leftTerm.eval(binding), self.rightTerm.eval(binding))
        except NameError:
            return True  # Name wasn't found, then it is a partial evaluation
        
        
class EqFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x == y)
        
        
class NotEqFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x != y)
        
        
class GreaterThanFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x > y)    
        
class SmallerThanFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x < y)        
        
class GreaterThanEqFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x >= y)    
        
class SmallerThanEqFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x <= y)

class BinaryLogicOpFormula(Formula):
    def __init__(self, leftFormula, rightFormula, binaryLogicOp):
        self.leftFormula = leftFormula
        self.rightFormula = rightFormula
        self.binaryLogicOp = binaryLogicOp
    
    def eval(self, binding: dict = {}):
        return self.binaryLogicOp(self.leftFormula.eval(binding), self.rightFormula.eval(binding))


class TrueFormula(Formula):
    def eval(self, binding : dict = {}):
        return True


class AndFormula(BinaryLogicOpFormula):
    def __init__(self, leftFormula, rightFormula):
        super().__init__(leftFormula, rightFormula, lambda x, y: x and y)