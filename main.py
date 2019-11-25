from CEP import *
from IOUtils import *

events = fileInput("NASDAQ_20080201_1_sorted.txt", 0)

pattern = Pattern(
SeqPatternStructure([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("AVID", "c")]), 
EqFormula(IdentifierTerm("s", lambda x: x[0]), AtomicTerm("AAPL"))
)

cep = CEP(Tree, [pattern], events)

fileOutput(cep.getPatternMatchStream())