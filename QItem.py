'''
This class is used to represent a "parameter" to the SEQ operator, which is formally called a qitem.
Event and Type are properties specified in SASE+.
Negation and Kleene Plus are modifiers specified in SASE+.
'''
class QItem:
    def __init__(self, eventType, name, kleenePlus=False, negated=False):
        self.__eventType = eventType
        self.__name = name
        self.__kleenePlus = kleenePlus
        self.__negated = negated
    
    def getType(self):
        return self.__eventType
    
    def getName(self):
        return self.__name
    
    def isKleenePlus(self):
        return self.__kleenePlus
    
    def isNegated(self):
        return self.__negated