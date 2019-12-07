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

"""
PATTERN SEQ(AppleStockPriceUpdate a, AmazonStockPriceUpdate b, AvidStockPriceUpdate c)
WHERE   a.OpeningPrice > b.OpeningPrice
    AND b.OpeningPrice > c.OpeningPrice
WITHIN 5 minutes
"""
pattern = Pattern(
    SeqOperator([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("AVID", "c")]), 
    AndFormula(
        GreaterThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
        GreaterThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
    timedelta(minutes=5) # Including
)
cep = CEP(Tree, [pattern], events)
fileOutput(cep.getPatternMatchStream(), 'matches.txt')
print("Finished processing simple pattern")

"""
This pattern is looking for a short ascend in the Google peak prices.
PATTERN SEQ(GoogleStockPriceUpdate a, GoogleStockPriceUpdate b, GoogleStockPriceUpdate c)
WHERE a.PeakPrice < b.PeakPrice AND b.PeakPrice < c.PeakPrice
WITHIN 3 minutes
"""
googleAscendPattern = Pattern(
    SeqOperator([QItem("GOOG", "a"), QItem("GOOG", "b"), QItem("GOOG", "c")]),
    AndFormula(
        SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
        SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"]))
    ),
    timedelta(minutes=3)
)
cep = CEP(Tree, [googleAscendPattern], events)
fileOutput(cep.getPatternMatchStream(), 'googleAscendMatches.txt')
print("Finished processing google ascend pattern")

"""
This pattern is looking for an in-stable day for Amazon.
PATTERN SEQ(AmazonStockPriceUpdate x1, AmazonStockPriceUpdate x2, AmazonStockPriceUpdate x3)
WHERE x1.LowestPrice <= 75 AND x2.PeakPrice >= 78 AND x3.LowestPrice <= x1.LowestPrice
WITHIN 1 day
"""
amazonInstablePattern = Pattern(
    SeqOperator([QItem("AMZN", "x1"), QItem("AMZN", "x2"), QItem("AMZN", "x3")]),
    AndFormula(
        SmallerThanEqFormula(IdentifierTerm("x1", lambda x: x["Lowest Price"]), AtomicTerm(75)),
        AndFormula(
            GreaterThanEqFormula(IdentifierTerm("x2", lambda x: x["Peak Price"]), AtomicTerm(78)),
            SmallerThanEqFormula(IdentifierTerm("x3", lambda x: x["Lowest Price"]), IdentifierTerm("x1", lambda x: x["Lowest Price"]))
        )
    ),
    timedelta(days=1)
)
cep = CEP(Tree, [amazonInstablePattern], events)
fileOutput(cep.getPatternMatchStream(), 'amazonInstableMatches.txt')
print("Finished processing amazon instable pattern")

"""
This pattern is looking for a race between driv and microsoft in ten minutes
PATTERN SEQ(MicrosoftStockPriceUpdate a, DrivStockPriceUpdate b, MicrosoftStockPriceUpdate c, DrivStockPriceUpdate d, MicrosoftStockPriceUpdate e)
WHERE a.PeakPrice < b.PeakPrice AND b.PeakPrice < c.PeakPrice AND c.PeakPrice < d.PeakPrice AND d.PeakPrice < e.PeakPrice
WITHIN 10 minutes
"""
msftDrivRacePattern = Pattern(
    SeqOperator([QItem("MSFT", "a"), QItem("DRIV", "b"), QItem("MSFT", "c"), QItem("DRIV", "d"), QItem("MSFT", "e")]),
    AndFormula(
        AndFormula(
            SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
            SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"]))
        ),
        AndFormula(
            SmallerThanFormula(IdentifierTerm("c", lambda x: x["Peak Price"]), IdentifierTerm("d", lambda x: x["Peak Price"])),
            SmallerThanFormula(IdentifierTerm("d", lambda x: x["Peak Price"]), IdentifierTerm("e", lambda x: x["Peak Price"]))
        )
    ),
    timedelta(minutes=10)
)
cep = CEP(Tree, [msftDrivRacePattern], events)
fileOutput(cep.getPatternMatchStream(), 'msftDrivRaceMatches.txt')
print("Finished processing msft-driv race pattern")

"""
This Pattern is looking for a 1% increase in the google stock in a half-hour.
PATTERN SEQ(GoogleStockPriceUpdate a, GoogleStockPriceUpdate b)
WHERE b.PeakPrice >= 1.01 * a.PeakPrice
WITHIN 30 minutes
"""
googleIncreasePattern = Pattern(
    SeqOperator([QItem("GOOG", "a"), QItem("GOOG", "b")]),
    GreaterThanEqFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), MulTerm(AtomicTerm(1.01), IdentifierTerm("a", lambda x: x["Peak Price"]))),
    timedelta(minutes=30)
)
cep = CEP(Tree, [googleIncreasePattern], events)
fileOutput(cep.getPatternMatchStream(), 'googleIncreaseMatches.txt')
print("Finished processing google increase pattern")

"""
This pattern is looking for an amazon stock in peak price of 73.
"""
amazonSpecificPattern = Pattern(
    SeqOperator([QItem("AMZN", "a")]),
    EqFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), AtomicTerm(73))
)
cep = CEP(Tree, [amazonSpecificPattern], events)
fileOutput(cep.getPatternMatchStream(), 'amazonSpecificMatches.txt')
print("Finished processing amazon specific pattern")