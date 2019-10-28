'''
Seq(A)
WHERE A.name = 'AAPL'
'''

from CEP import *

events = Event.fileInput("NASDAQ_20080201_1_sorted.txt")
print(events[0].event)

query = Query(
[QItem("Stock", "s")], 
EqFormula(IdentifierTerm("s", lambda x: x[0]), AtomicTerm("AAPL"))
)

cep = CEP(events)
result = cep.findPattern(query, Tree, False)

Tree.eval(0, 0)

print(result)