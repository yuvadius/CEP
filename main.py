from CEP import *
from IOUtils import *
from Utils import *
from OrderBasedAlgorithms import *
from time import time
from datetime import timedelta

nasdaqEventStream = fileInput("NASDAQ_20080201_1_sorted.txt", 
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

def closeFiles(file1, file2):
    file1.close()
    file2.close()

def fileCompare(pathA, pathB):
    file1 = open(pathA)
    file2 = open(pathB)
    file1List = [] # List of unique patterns
    file2List = [] # List of unique patterns
    lineStack = ""
    for line in file1:
        if not line.strip():
            lineStack += line
        elif not (lineStack in file1List):
            file1List.append(lineStack)
            lineStack = ""
    lineStack = ""
    for line in file2:
        if not line.strip():
            lineStack += line
        elif not (lineStack in file2List):
            file2List.append(lineStack)
            lineStack = ""
    if len(file1List) != len(file2List): # Fast check
        closeFiles(file1, file2)
        return False
    for line in file1List:
        if not (line in file2List):
            closeFiles(file1, file2)
            return False
    for line in file2List:
        if not (line in file1List):
            closeFiles(file1, file2)
            return False
    closeFiles(file1, file2)
    return True

def createTest(testName, patterns, algorithm = TrivialAlgorithm()):
    events = nasdaqEventStream.duplicate()
    cep = CEP(algorithm, patterns, events)
    fileOutput(cep.getPatternMatchContainer(), '../TestsExpected/%sMatches.txt' % testName)
    print("Finished creating test %s" % testName)

def runTest(testName, patterns, algorithm = TrivialAlgorithm()):
    events = nasdaqEventStream.duplicate()
    cep = CEP(algorithm, patterns, events)
    match = cep.getPatternMatchContainer()
    timeTaken = cep.getElapsed()
    fileOutput(match, '%sMatches.txt' % testName)
    print("Test %s result: %s, Time Passed: %s" % (testName, 
        "Succeeded" if fileCompare("Matches/%sMatches.txt" % testName, "TestsExpected/%sMatches.txt" % testName) else "Failed", timeTaken))


def simplePatternSearch():
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
        timedelta(minutes=5)
    )
    runTest("simple", [pattern])

def googleAscendPatternSearch():
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
    runTest('googleAscend', [googleAscendPattern])

def amazonInstablePatternSearch():
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
    runTest('amazonInstable', [amazonInstablePattern])

def msftDrivRacePatternSearch():
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
    runTest('msftDrivRace', [msftDrivRacePattern])

def googleIncreasePatternSearch():
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
    runTest('googleIncrease', [googleIncreasePattern])

def amazonSpecificPatternSearch():
    """
    This pattern is looking for an amazon stock in peak price of 73.
    """
    amazonSpecificPattern = Pattern(
        SeqOperator([QItem("AMZN", "a")]),
        EqFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), AtomicTerm(73))
    )
    runTest('amazonSpecific', [amazonSpecificPattern])

def googleAmazonLowPatternSearch():
    """
    This pattern is looking for low prices of Amazon and Google at the same minute.
    PATTERN AND(AmazonStockPriceUpdate a, GoogleStockPriceUpdate g)
    WHERE a.PeakPrice <= 73 AND g.PeakPrice <= 525
    WITHIN 1 minute
    """
    googleAmazonLowPattern = Pattern(
        AndOperator([QItem("AMZN", "a"), QItem("GOOG", "g")]),
        AndFormula(
            SmallerThanEqFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), AtomicTerm(73)),
            SmallerThanEqFormula(IdentifierTerm("g", lambda x: x["Peak Price"]), AtomicTerm(525))
        ),
        timedelta(minutes=1)
    )
    runTest('googleAmazonLow', [googleAmazonLowPattern])

def nonsensePatternSearch():
    """
    This pattern is looking for something that does not make sense.
    PATTERN AND(AmazonStockPriceUpdate a, AvidStockPriceUpdate b, AppleStockPriceUpdate c)
    WHERE a.PeakPrice < b.PeakPrice AND b.PeakPrice < c.PeakPrice AND c.PeakPrice < a.PeakPrice
    """
    nonsensePattern = Pattern(
        AndOperator([QItem("AMZN", "a"), QItem("AVID", "b"), QItem("AAPL", "c")]),
        AndFormula(
            SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
            AndFormula(
                SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"])),
                SmallerThanFormula(IdentifierTerm("c", lambda x: x["Peak Price"]), IdentifierTerm("a", lambda x: x["Peak Price"]))
            )
        ),
        timedelta(minutes=1)
    )
    runTest('nonsense', [nonsensePattern])

def hierarchyPatternSearch():
    """
    The following pattern is looking for Amazon < Apple < Google cases in one minute windows.
    PATTERN AND(AmazonStockPriceUpdate a, AppleStockPriceUpdate b, GoogleStockPriceUpdate c)
    WHERE a.PeakPrice < b.PeakPrice AND b.PeakPrice < c.PeakPrice
    WITHIN 1 minute
    """
    hierarchyPattern = Pattern(
        AndOperator([QItem("AMZN", "a"), QItem("AAPL", "b"), QItem("GOOG", "c")]),
        AndFormula(
            SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
            SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"]))
        ),
        timedelta(minutes=1)
    )
    runTest('hierarchy', [hierarchyPattern])

def multiplePatternSearch():
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
    googleAscendPattern = Pattern(
        SeqOperator([QItem("GOOG", "a"), QItem("GOOG", "b"), QItem("GOOG", "c")]),
        AndFormula(
            SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
            SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"]))
        ),
        timedelta(minutes=3)
    )
    createTest('multiplePatterns', [amazonInstablePattern, googleAscendPattern])
    print("Created the output as test, because output is non-deterministic. Should check manually.")

def nonFrequencyPatternSearch():
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("LOCM", "c")]), 
        AndFormula(
            GreaterThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
            GreaterThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
        timedelta(minutes=5)
    )
    runTest("nonFrequency", [pattern])

def frequencyPatternSearch():
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("LOCM", "c")]), 
        AndFormula(
            GreaterThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
            GreaterThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
        timedelta(minutes=5)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"AAPL": 460, "AMZN": 442, "LOCM": 219})
    runTest("frequency", [pattern], AscendingFrequencyAlgorithm())

def nonFrequencyPatternSearch2():
    pattern = Pattern(
        SeqOperator([QItem("LOCM", "a"), QItem("AMZN", "b"), QItem("AAPL", "c")]), 
        AndFormula(
            SmallerThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
            SmallerThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
        timedelta(minutes=5)
    )
    runTest("nonFrequency2", [pattern])

def frequencyPatternSearch2():
    pattern = Pattern(
        SeqOperator([QItem("LOCM", "a"), QItem("AMZN", "b"), QItem("AAPL", "c")]), 
        AndFormula(
            SmallerThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
            SmallerThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
        timedelta(minutes=5)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"AAPL": 2, "AMZN": 3, "LOCM": 1})
    runTest("frequency2", [pattern], AscendingFrequencyAlgorithm())

def nonFrequencyPatternSearch3():
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AAPL", "b"), QItem("AAPL", "c"), QItem("LOCM", "d")]), 
        None,
        timedelta(minutes=5)
    )
    runTest("nonFrequency3", [pattern])

def frequencyPatternSearch3():
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AAPL", "b"), QItem("AAPL", "c"), QItem("LOCM", "d")]), 
        None,
        timedelta(minutes=5)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"AAPL": 460, "LOCM": 219})
    runTest("frequency3", [pattern], AscendingFrequencyAlgorithm())

def nonFrequencyPatternSearch4():
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("AVID", "c"), QItem("LOCM", "d")]), 
        None,
        timedelta(minutes=7)
    )
    runTest("nonFrequency4", [pattern])

def frequencyPatternSearch4():
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("AVID", "c"), QItem("LOCM", "d")]), 
        None,
        timedelta(minutes=7)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"AVID": 1, "LOCM": 2, "AAPL": 3, "AMZN": 4})
    runTest("frequency4", [pattern], AscendingFrequencyAlgorithm())

def nonFrequencyPatternSearch5():
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a1"), QItem("LOCM", "b1"), QItem("AAPL", "a2"), QItem("LOCM", "b2"), QItem("AAPL", "a3"), QItem("LOCM", "b3")]), 
        None,
        timedelta(minutes=7)
    )
    runTest("nonFrequency5", [pattern])

def frequencyPatternSearch5():
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a1"), QItem("LOCM", "b1"), QItem("AAPL", "a2"), QItem("LOCM", "b2"), QItem("AAPL", "a3"), QItem("LOCM", "b3")]), 
        None,
        timedelta(minutes=7)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"LOCM": 1, "AAPL": 2}) # {"AAPL": 460, "LOCM": 219}
    runTest("frequency5", [pattern], AscendingFrequencyAlgorithm())
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a1"), QItem("LOCM", "b1"), QItem("AAPL", "a2"), QItem("LOCM", "b2"), QItem("AAPL", "a3"), QItem("LOCM", "b3")]), 
        None,
        timedelta(minutes=7)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"AAPL": 1, "LOCM": 2}) # {"AAPL": 460, "LOCM": 219}
    runTest("frequency5", [pattern], AscendingFrequencyAlgorithm())


def greedyPatternSearch():
    pattern = Pattern(
        SeqOperator([QItem("MSFT", "a"), QItem("DRIV", "b"), QItem("ORLY", "c"), QItem("CBRL", "d")]),
        AndFormula(
            AndFormula(
                SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
                SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"]))
            ),
            SmallerThanFormula(IdentifierTerm("c", lambda x: x["Peak Price"]), IdentifierTerm("d", lambda x: x["Peak Price"]))
        ),
        timedelta(minutes=3)
    )
    selectivtyMatrix = [[1.0, 0.9458241432977189, 1.0, 1.0], [0.9458241432977189, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9990885787524921], [1.0, 1.0, 0.9990885787524921, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivtyMatrix, arrivalRates))
    runTest('greedy1', [pattern], GreedyAlgorithm())


def iiRandomPatternSearch():
    pattern = Pattern(
        SeqOperator([QItem("MSFT", "a"), QItem("DRIV", "b"), QItem("ORLY", "c"), QItem("CBRL", "d")]),
        AndFormula(
            AndFormula(
                SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
                SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"]))
            ),
            SmallerThanFormula(IdentifierTerm("c", lambda x: x["Peak Price"]), IdentifierTerm("d", lambda x: x["Peak Price"]))
        ),
        timedelta(minutes=3)
    )
    selectivtyMatrix = [[1.0, 0.9458241432977189, 1.0, 1.0], [0.9458241432977189, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9990885787524921], [1.0, 1.0, 0.9990885787524921, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivtyMatrix, arrivalRates))
    print("Might fail: order is non-deterministic")
    runTest('iiRandom1', [pattern], IIRandomAlgorithm(IterativeImprovementType.SWAP_BASED))

def iiRandom2PatternSearch():
    pattern = Pattern(
        SeqOperator([QItem("MSFT", "a"), QItem("DRIV", "b"), QItem("ORLY", "c"), QItem("CBRL", "d")]),
        AndFormula(
            AndFormula(
                SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
                SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"]))
            ),
            SmallerThanFormula(IdentifierTerm("c", lambda x: x["Peak Price"]), IdentifierTerm("d", lambda x: x["Peak Price"]))
        ),
        timedelta(minutes=3)
    )
    selectivtyMatrix = [[1.0, 0.9458241432977189, 1.0, 1.0], [0.9458241432977189, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9990885787524921], [1.0, 1.0, 0.9990885787524921, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivtyMatrix, arrivalRates))
    print("Might fail: order is non-deterministic")
    runTest('iiRandom2', [pattern], IIRandomAlgorithm(IterativeImprovementType.CIRCLE_BASED))

def iiGreedyPatternSearch():
    pattern = Pattern(
        SeqOperator([QItem("MSFT", "a"), QItem("DRIV", "b"), QItem("ORLY", "c"), QItem("CBRL", "d")]),
        AndFormula(
            AndFormula(
                SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
                SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"]))
            ),
            SmallerThanFormula(IdentifierTerm("c", lambda x: x["Peak Price"]), IdentifierTerm("d", lambda x: x["Peak Price"]))
        ),
        timedelta(minutes=3)
    )
    selectivtyMatrix = [[1.0, 0.9458241432977189, 1.0, 1.0], [0.9458241432977189, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9990885787524921], [1.0, 1.0, 0.9990885787524921, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivtyMatrix, arrivalRates))
    runTest('iiGreedy1', [pattern], IIGreedyAlgorithm(IterativeImprovementType.SWAP_BASED))

def iiGreedy2PatternSearch():
    pattern = Pattern(
        SeqOperator([QItem("MSFT", "a"), QItem("DRIV", "b"), QItem("ORLY", "c"), QItem("CBRL", "d")]),
        AndFormula(
            AndFormula(
                SmallerThanFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), IdentifierTerm("b", lambda x: x["Peak Price"])),
                SmallerThanFormula(IdentifierTerm("b", lambda x: x["Peak Price"]), IdentifierTerm("c", lambda x: x["Peak Price"]))
            ),
            SmallerThanFormula(IdentifierTerm("c", lambda x: x["Peak Price"]), IdentifierTerm("d", lambda x: x["Peak Price"]))
        ),
        timedelta(minutes=3)
    )
    selectivtyMatrix = [[1.0, 0.9458241432977189, 1.0, 1.0], [0.9458241432977189, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9990885787524921], [1.0, 1.0, 0.9990885787524921, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivtyMatrix, arrivalRates))
    runTest('iiGreedy2', [pattern], IIGreedyAlgorithm(IterativeImprovementType.CIRCLE_BASED))

'''
simplePatternSearch()
googleAscendPatternSearch()
amazonInstablePatternSearch()
msftDrivRacePatternSearch()
googleIncreasePatternSearch()
amazonSpecificPatternSearch()
googleAmazonLowPatternSearch()
nonsensePatternSearch()
hierarchyPatternSearch()
nonFrequencyPatternSearch()
frequencyPatternSearch()
nonFrequencyPatternSearch2()
frequencyPatternSearch2()
nonFrequencyPatternSearch3()
frequencyPatternSearch3()
nonFrequencyPatternSearch4()
frequencyPatternSearch4()
nonFrequencyPatternSearch5()
frequencyPatternSearch5()
greedyPatternSearch()
iiRandomPatternSearch()
iiRandom2PatternSearch()
'''

iiGreedyPatternSearch()
iiGreedy2PatternSearch()