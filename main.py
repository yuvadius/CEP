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
    StrictSeqPatternStructure([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("AVID", "c")]), 
    AndFormula(
        GreaterThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
        GreaterThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
    timedelta(seconds=60)
)

cep = CEP(Tree, [pattern], events)

fileOutput(cep.getPatternMatchStream())
