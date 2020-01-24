from abc import ABC  # Abstract Base Class


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
    
    def getTermOf(self, names : set):
        return self
        
class IdentifierTerm(Term):
    def __init__(self, name: str, getAttrFunc):
        self.name = name
        self.getAttrFunc = getAttrFunc
    
    def eval(self, binding: dict = {}):
        if not type(binding) == dict or not self.name in binding:
            raise NameError("Name %s is not bound to a value" % self.name)
        return self.getAttrFunc(binding[self.name])
    
    def getTermOf(self, names : set):
        if self.name in names:
            return self
        else:
            return None
        
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
    
    def getTermOf(self, names : set):
        lhs = self.lhs.getTermOf(names)
        rhs = self.rhs.getTermOf(names)
        if lhs and rhs:
            return PlusTerm(lhs, rhs)
        else:
            return None
        
class MinusTerm(BinaryOperationTerm):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs, lambda x, y: x - y)
    
    def getTermOf(self, names : set):
        lhs = self.lhs.getTermOf(names)
        rhs = self.rhs.getTermOf(names)
        if lhs and rhs:
            return MinusTerm(lhs, rhs)
        else:
            return None
        
class MulTerm(BinaryOperationTerm):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs, lambda x, y: x * y)
    
    def getTermOf(self, names : set):
        lhs = self.lhs.getTermOf(names)
        rhs = self.rhs.getTermOf(names)
        if lhs and rhs:
            return MulTerm(lhs, rhs)
        else:
            return None
        
class DivTerm(BinaryOperationTerm):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs, lambda x, y: x / y)
    
    def getTermOf(self, names : set):
        lhs = self.lhs.getTermOf(names)
        rhs = self.rhs.getTermOf(names)
        if lhs and rhs:
            return DivTerm(lhs, rhs)
        else:
            return None
        
class Formula(ABC):
    '''
    Returns whether the parameters satisfy the formula. It evaluates to True or False.
    If there are variables (identifiers) in the formula, a name-value binding shall be inputted.
    '''
    def eval(self, binding: dict = {}):
        pass

    @staticmethod
    def getIdentifiers(formulaOrTerm):
        identifiers = []
        for attribute in dir(formulaOrTerm):
            if (type(getattr(formulaOrTerm,attribute)) == IdentifierTerm):
                identifiers.append(getattr(formulaOrTerm,attribute).name)
            elif (issubclass(type(getattr(formulaOrTerm,attribute)), Formula) or issubclass(type(getattr(formulaOrTerm,attribute)), Term)):
                identifiers = identifiers + Formula.getIdentifiers(getattr(formulaOrTerm,attribute))
        return list(dict.fromkeys(identifiers)) # Remove duplicates
    
    def getFormulaOf(self, names : set):
        pass

    @staticmethod
    def splitAndFormulas(formula):
        if (type(formula) == AndFormula):
            return Formula.splitAndFormulas(formula.leftFormula) + Formula.splitAndFormulas(formula.rightFormula)
        return [formula]

class AtomicFormula(Formula):
    def __init__(self, leftTerm, rightTerm, relBinOp):
        self.leftTerm = leftTerm
        self.rightTerm = rightTerm
        self.relBinOp = relBinOp
    
    def eval(self, binding: dict = {}):
        return self.relBinOp(self.leftTerm.eval(binding), self.rightTerm.eval(binding))
        
class EqFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x == y)
    
    
    def getFormulaOf(self, names : set):
        rightTerm = self.rightTerm.getTermOf(names)
        leftTerm = self.leftTerm.getTermOf(names)
        if leftTerm and rightTerm:
            return EqFormula(leftTerm, rightTerm)
        else:
            return None
        
class NotEqFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x != y)
    
    def getFormulaOf(self, names : set):
        rightTerm = self.rightTerm.getTermOf(names)
        leftTerm = self.leftTerm.getTermOf(names)
        if leftTerm and rightTerm:
            return NotEqFormula(leftTerm, rightTerm)
        else:
            return None
        
class GreaterThanFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x > y)    
    
    def getFormulaOf(self, names : set):
        rightTerm = self.rightTerm.getTermOf(names)
        leftTerm = self.leftTerm.getTermOf(names)
        if leftTerm and rightTerm:
            return GreaterThanFormula(leftTerm, rightTerm)
        else:
            return None

class SmallerThanFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x < y)        
    
    def getFormulaOf(self, names : set):
        rightTerm = self.rightTerm.getTermOf(names)
        leftTerm = self.leftTerm.getTermOf(names)
        if leftTerm and rightTerm:
            return SmallerThanFormula(leftTerm, rightTerm)
        else:
            return None
    
class GreaterThanEqFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x >= y)

    def getFormulaOf(self, names : set):
        rightTerm = self.rightTerm.getTermOf(names)
        leftTerm = self.leftTerm.getTermOf(names)
        if leftTerm and rightTerm:
            return GreaterThanEqFormula(leftTerm, rightTerm)
        else:
            return None 
        
class SmallerThanEqFormula(AtomicFormula):
    def __init__(self, leftTerm, rightTerm):
        super().__init__(leftTerm, rightTerm, lambda x, y: x <= y)
    
    def getFormulaOf(self, names : set):
        rightTerm = self.rightTerm.getTermOf(names)
        leftTerm = self.leftTerm.getTermOf(names)
        if leftTerm and rightTerm:
            return SmallerThanEqFormula(leftTerm, rightTerm)
        else:
            return None

class BinaryLogicOpFormula(Formula):
    def __init__(self, leftFormula, rightFormula, binaryLogicOp):
        self.leftFormula = leftFormula
        self.rightFormula = rightFormula
        self.binaryLogicOp = binaryLogicOp
    
    def eval(self, binding: dict = {}):
        return self.binaryLogicOp(self.leftFormula.eval(binding), self.rightFormula.eval(binding))

class AndFormula(BinaryLogicOpFormula):
    def __init__(self, leftFormula, rightFormula):
        super().__init__(leftFormula, rightFormula, lambda x, y: x and y)

    def getFormulaOf(self, names : set):
        rightFormula = self.rightFormula.getFormulaOf(names)
        leftFormula = self.leftFormula.getFormulaOf(names)
        if leftFormula and rightFormula:
            return AndFormula(leftFormula, rightFormula)
        elif leftFormula:
            return leftFormula
        elif rightFormula:
            return rightFormula
        else:
            return None

class TrueFormula(Formula):
    def __init__(self):
        pass

    def eval(self, binding: dict = {}):
        return True
