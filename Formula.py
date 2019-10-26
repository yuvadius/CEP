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
    def eval(self, binding={}):
        pass


class AtomicTerm(Term):
    def __init__(self, value):
        self.__value = value
    
    def eval(self, binding={}):
        return self.__value

        
class IdentifierTerm(Term):
    def __init__(self, name, getAttrFunc):
        self.__name = name
        self.__getAttrFunc = getAttrFunc
    
    def eval(self, binding={}):
        if not type(binding) == dict or not self.__name in binding:
            raise NameError("Name %s is not bound to a value" % self.__name)
        return self.__getAttrFunc(binding[self.__name])

        
class BinaryOperationTerm(Term):
    def __init__(self, lhs, rhs, binOp):
        self.__lhs = lhs
        self.__rhs = rhs
        self.__binOp = binOp
    
    def eval(self, binding={}):
        return self.__binOp(self.__lhs.eval(binding), self.__rhs.eval(binding))

        
class PlusTerm(Term):
    def __init__(self, lhs, rhs):
        self.__term = BinaryOperationTerm(lhs, rhs, lambda x, y: x + y)
    
    def eval(self, binding={}):
        return self.__term.eval(binding)

        
class MinusTerm(Term):
    def __init__(self, lhs, rhs):
        self.__term = BinaryOperationTerm(lhs, rhs, lambda x, y: x - y)
    
    def eval(self, binding={}):
        return self.__term.eval(binding)

        
class MulTerm(Term):
    def __init__(self, lhs, rhs):
        self.__term = BinaryOperationTerm(lhs, rhs, lambda x, y: x * y)
    
    def eval(self, binding={}):
        return self.__term.eval(binding)

        
class DivTerm(Term):
    def __init__(self, lhs, rhs):
        self.__term = BinaryOperationTerm(lhs, rhs, lambda x, y: x / y)
    
    def eval(self, binding={}):
        return self.__term.eval(binding)

        
class Formula(ABC):
    '''
    Returns whether the parameters satisfy the formula. It evaluates to True or False.
    If there are variables (identifiers) in the formula, a name-value binding shall be inputted.
    '''
    def eval(self, binding={}):
        pass

        
class AtomicFormula(Formula):
    def __init__(self, leftTerm, rightTerm, relBinOp):
        self.__leftTerm = leftTerm
        self.__rightTerm = rightTerm
        self.__relBinOp = relBinOp
    
    def eval(self, binding={}):
        return self.__relBinOp(self.__leftTerm.eval(binding), self.__rightTerm.eval(binding))
        
        
class EqFormula(Formula):
    def __init__(self, leftTerm, rightTerm):
        self.__formula = AtomicFormula(leftTerm, rightTerm, lambda x, y: x == y)
    
    def eval(self, binding={}):
        return self.__formula.eval(binding)
        
        
class NotEqFormula(Formula):
    def __init__(self, leftTerm, rightTerm):
        self.__formula = AtomicFormula(leftTerm, rightTerm, lambda x, y: x != y)
    
    def eval(self, binding={}):
        return self.__formula.eval(binding)
        
        
class GreaterThanFormula(Formula):
    def __init__(self, leftTerm, rightTerm):
        self.__formula = AtomicFormula(leftTerm, rightTerm, lambda x, y: x > y)
    
    def eval(self, binding={}):
        return self.__formula.eval(binding)        
        
class SmallerThanFormula(Formula):
    def __init__(self, leftTerm, rightTerm):
        self.__formula = AtomicFormula(leftTerm, rightTerm, lambda x, y: x < y)
    
    def eval(self, binding={}):
        return self.__formula.eval(binding)        
        
class GreaterThanEqFormula(Formula):
    def __init__(self, leftTerm, rightTerm):
        self.__formula = AtomicFormula(leftTerm, rightTerm, lambda x, y: x >= y)
    
    def eval(self, binding={}):
        return self.__formula.eval(binding)        
        
class SmallerThanEqFormula(Formula):
    def __init__(self, leftTerm, rightTerm):
        self.__formula = AtomicFormula(leftTerm, rightTerm, lambda x, y: x <= y)
    
    def eval(self, binding={}):
        return self.__formula.eval(binding)

class BinaryLogicOpFormula(Formula):
    def __init__(self, leftFormula, rightFormula, binaryLogicOp):
        self.__leftFormula = leftFormula
        self.__rightFormula = rightFormula
        self.__binaryLogicOp = binaryLogicOp
    
    def eval(self, binding={}):
        return self.__binaryLogicOp(self.__leftFormula.eval(binding), self.__rightFormula.eval(binding))

class AndFormula(Formula):
    def __init__(self, leftFormula, rightFormula):
        self.__formula = BinaryLogicOpFormula(leftFormula, rightFormula, lambda x, y: x and y)
    
    def eval(self, binding={}):
        return self.__formula.eval(binding)