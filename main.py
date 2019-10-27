from CEP import *

p1 = CEP(Event.fileInput("NASDAQ_20080201_1_sorted.txt"))

x = AndFormula(EqFormula(AtomicTerm(5), IdentifierTerm("Moti", lambda x: x["age"])), SmallerThanEqFormula(AtomicTerm(13), MulTerm(AtomicTerm(5), AtomicTerm(3))))
print(x.eval({ "Moti" : { "age": 5 } }))  # True
print(x.eval({ "Moti" : { "age": 31 } }))  # False