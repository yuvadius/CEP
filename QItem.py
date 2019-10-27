'''
This class is used to represent a "parameter" to the SEQ operator, which is formally called a qitem.
Event and Type are properties specified in SASE+.
Negation and Kleene Plus are modifiers specified in SASE+.
'''
class QItem:
    def __init__(self, eventType, name, kleenePlus=False, negated=False):
        self.eventType = eventType
        self.name = name
        self.kleenePlus = kleenePlus
        self.negated = negated