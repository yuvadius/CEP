from CEP import *

events = Event.fileInput("NASDAQ_20080201_1_sorted.txt", 0)
print(events[0].event)

query = Query(
StrictSequencePatternStructure([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("AVID", "c")]), 
EqFormula(IdentifierTerm("s", lambda x: x[0]), AtomicTerm("AAPL"))
)

cep = CEP(events)
result = cep.findPattern(query, Tree, False)

print(result)
