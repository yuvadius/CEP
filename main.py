from CEP import *
from IOUtils import *

events = fileInput("NASDAQ_20080201_1_sorted.txt", 
    [
        "Stock Ticker", 
        "Date", 
        "Opening Price", 
        "Peak Price", 
        "Lowest Price", 
        "Close Price", 
        "Volume"],
    "Stock Ticker",
    "Date")

pattern = Pattern(
    StrictSeqPatternStructure([QItem("YHOO", "a"), QItem("AAPL", "b"), QItem("AKAM", "c")]), 
    AndFormula(
        SmallerThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
        GreaterThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
    timedelta(seconds=60)
)

cep = CEP(Tree, [pattern], events)

fileOutput(cep.getPatternMatchStream())
