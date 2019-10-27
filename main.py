from CEP import *

event = Event.fileInput("NASDAQ_20080201_1_sorted.txt")
print(event[0].event)

'''
x = AndFormula(EqFormula(AtomicTerm(5), IdentifierTerm("Moti", lambda x: x["age"])), SmallerThanEqFormula(AtomicTerm(13), MulTerm(AtomicTerm(5), AtomicTerm(3))))
print(x.eval({ "Moti" : { "age": 5 } }))  # True
print(x.eval({ "Moti" : { "age": 31 } }))  # False

'''