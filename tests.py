from CEP import *
from IOUtils import *
from Utils import *
from OrderBasedAlgorithms import *
from time import time
from datetime import timedelta
from Statistics import *

nasdaqEventStreamShort = fileInput("NASDAQ_SHORT.txt", 
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
nasdaqEventStreamMedium = fileInput("NASDAQ_MEDIUM.txt", 
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
nasdaqEventStreamFrequencyTailored = fileInput("NASDAQ_FREQUENCY_TAILORED.txt", 
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
nasdaqEventStream_AAPL_AMZN_GOOG = fileInput("NASDAQ_AAPL_AMZN_GOOG.txt", 
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

nasdaqEventStream = fileInput("EventFiles/NASDAQ_LONG.txt", 
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

def createTest(testName, patterns, algorithm = TrivialAlgorithm(), events=None):
    if events == None:
        events = nasdaqEventStream.duplicate()
    else:
        events = events.duplicate()
    pattern = patterns[0]
    argsNum = len(pattern.patternStructure.args)
    matches = generateMatches(pattern, events)
    fileOutput(matches, '../TestsExpected/%sMatches.txt' % testName)
    print("Finished creating test %s" % testName)

def runTest(testName, patterns, createTestFile = False, algorithm = TrivialAlgorithm(), events = None):
    if createTestFile:
        createTest(testName, patterns, algorithm, events)
    if events == None:
        events = nasdaqEventStream.duplicate()
    else:
        events = events.duplicate()
    cep = CEP(algorithm, patterns, events)
    matches = cep.getPatternMatchContainer()
    timeTaken = cep.getElapsed()
    fileOutput(matches, '%sMatches.txt' % testName)
    print("Test %s result: %s, Time Passed: %s" % (testName, 
        "Succeeded" if fileCompare("Matches/%sMatches.txt" % testName, "TestsExpected/%sMatches.txt" % testName) else "Failed", timeTaken))

def oneArgumentsearchTest(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a")]), 
        GreaterThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), AtomicTerm(135)),
        timedelta.max
    )
    runTest("one", [pattern], createTestFile)

def simplePatternSearchTest(createTestFile = False):
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
    runTest("simple", [pattern], createTestFile)

def googleAscendPatternSearchTest(createTestFile = False):
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
    runTest('googleAscend', [googleAscendPattern], createTestFile)

def amazonInstablePatternSearchTest(createTestFile = False):
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
    runTest('amazonInstable', [amazonInstablePattern], createTestFile)

def msftDrivRacePatternSearchTest(createTestFile = False):
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
    runTest('msftDrivRace', [msftDrivRacePattern], createTestFile)

def googleIncreasePatternSearchTest(createTestFile = False):
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
    runTest('googleIncrease', [googleIncreasePattern], createTestFile)

def amazonSpecificPatternSearchTest(createTestFile = False):
    """
    This pattern is looking for an amazon stock in peak price of 73.
    """
    amazonSpecificPattern = Pattern(
        SeqOperator([QItem("AMZN", "a")]),
        EqFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), AtomicTerm(73))
    )
    runTest('amazonSpecific', [amazonSpecificPattern], createTestFile)

def googleAmazonLowPatternSearchTest(createTestFile = False):
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
    runTest('googleAmazonLow', [googleAmazonLowPattern], createTestFile)

def nonsensePatternSearchTest(createTestFile = False):
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
    runTest('nonsense', [nonsensePattern], createTestFile)

def hierarchyPatternSearchTest(createTestFile = False):
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
    runTest('hierarchy', [hierarchyPattern], createTestFile)

def multiplePatternSearchTest(createTestFile = False):
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
    runTest('multiplePatterns', [amazonInstablePattern, googleAscendPattern], createTestFile)

def nonFrequencyPatternSearchTest(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("LOCM", "c")]), 
        AndFormula(
            GreaterThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
            GreaterThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
        timedelta(minutes=5)
    )
    runTest("nonFrequency", [pattern], createTestFile)

def frequencyPatternSearchTest(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("LOCM", "c")]), 
        AndFormula(
            GreaterThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
            GreaterThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
        timedelta(minutes=5)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"AAPL": 460, "AMZN": 442, "LOCM": 219})
    runTest("frequency", [pattern], createTestFile, AscendingFrequencyAlgorithm())

def nonFrequencyPatternSearch2Test(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("LOCM", "a"), QItem("AMZN", "b"), QItem("AAPL", "c")]), 
        AndFormula(
            SmallerThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
            SmallerThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
        timedelta(minutes=5)
    )
    runTest("nonFrequency2", [pattern], createTestFile)

def frequencyPatternSearch2Test(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("LOCM", "a"), QItem("AMZN", "b"), QItem("AAPL", "c")]), 
        AndFormula(
            SmallerThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])), 
            SmallerThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))),
        timedelta(minutes=5)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"AAPL": 2, "AMZN": 3, "LOCM": 1})
    runTest("frequency2", [pattern], createTestFile, AscendingFrequencyAlgorithm())

def nonFrequencyPatternSearch3Test(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AAPL", "b"), QItem("AAPL", "c"), QItem("LOCM", "d")]), 
        TrueFormula(),
        timedelta(minutes=5)
    )
    runTest("nonFrequency3", [pattern], createTestFile)

def frequencyPatternSearch3Test(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AAPL", "b"), QItem("AAPL", "c"), QItem("LOCM", "d")]), 
        TrueFormula(),
        timedelta(minutes=5)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"AAPL": 460, "LOCM": 219})
    runTest("frequency3", [pattern], createTestFile, AscendingFrequencyAlgorithm())

def nonFrequencyPatternSearch4Test(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("AVID", "c"), QItem("LOCM", "d")]), 
        TrueFormula(),
        timedelta(minutes=7)
    )
    runTest("nonFrequency4", [pattern], createTestFile)

def frequencyPatternSearch4Test(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("AVID", "c"), QItem("LOCM", "d")]), 
        TrueFormula(),
        timedelta(minutes=7)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"AVID": 1, "LOCM": 2, "AAPL": 3, "AMZN": 4})
    runTest("frequency4", [pattern], createTestFile, AscendingFrequencyAlgorithm())

def nonFrequencyPatternSearch5Test(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a1"), QItem("LOCM", "b1"), QItem("AAPL", "a2"), QItem("LOCM", "b2"), QItem("AAPL", "a3"), QItem("LOCM", "b3")]), 
        TrueFormula(),
        timedelta(minutes=7)
    )
    runTest("nonFrequency5", [pattern], createTestFile)

def frequencyPatternSearch5Test(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a1"), QItem("LOCM", "b1"), QItem("AAPL", "a2"), QItem("LOCM", "b2"), QItem("AAPL", "a3"), QItem("LOCM", "b3")]), 
        TrueFormula(),
        timedelta(minutes=7)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"LOCM": 1, "AAPL": 2}) # {"AAPL": 460, "LOCM": 219}
    runTest("frequency5", [pattern], createTestFile, AscendingFrequencyAlgorithm())
    
def frequencyPatternSearch6Test(createTestFile = False):    
    pattern = Pattern(
        SeqOperator([QItem("AAPL", "a1"), QItem("LOCM", "b1"), QItem("AAPL", "a2"), QItem("LOCM", "b2"), QItem("AAPL", "a3"), QItem("LOCM", "b3")]), 
        TrueFormula(),
        timedelta(minutes=7)
    )
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, {"AAPL": 1, "LOCM": 2}) # {"AAPL": 460, "LOCM": 219}
    runTest("frequency6", [pattern], createTestFile, AscendingFrequencyAlgorithm())

def greedyPatternSearchTest(createTestFile = False):
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
    selectivityMatrix = [[1.0, 0.9457796098355941, 1.0, 1.0], [0.9457796098355941, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9992557393942864], [1.0, 1.0, 0.9992557393942864, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivityMatrix, arrivalRates))
    runTest('greedy1', [pattern], createTestFile, GreedyAlgorithm(), nasdaqEventStream)

def iiRandomPatternSearchTest(createTestFile = False):
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
    selectivityMatrix = [[1.0, 0.9457796098355941, 1.0, 1.0], [0.9457796098355941, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9992557393942864], [1.0, 1.0, 0.9992557393942864, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivityMatrix, arrivalRates))
    runTest('iiRandom1', [pattern], createTestFile, IIRandomAlgorithm(IterativeImprovementType.SWAP_BASED), nasdaqEventStream)

def iiRandom2PatternSearchTest(createTestFile = False):
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
    selectivityMatrix = [[1.0, 0.9457796098355941, 1.0, 1.0], [0.9457796098355941, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9992557393942864], [1.0, 1.0, 0.9992557393942864, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivityMatrix, arrivalRates))
    runTest('iiRandom2', [pattern], createTestFile, IIRandomAlgorithm(IterativeImprovementType.CIRCLE_BASED), nasdaqEventStream)

def iiGreedyPatternSearchTest(createTestFile = False):
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
    selectivityMatrix = [[1.0, 0.9457796098355941, 1.0, 1.0], [0.9457796098355941, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9992557393942864], [1.0, 1.0, 0.9992557393942864, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivityMatrix, arrivalRates))
    runTest('iiGreedy1', [pattern], createTestFile, IIGreedyAlgorithm(IterativeImprovementType.SWAP_BASED), nasdaqEventStream)

def iiGreedy2PatternSearchTest(createTestFile = False):
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
    selectivityMatrix = [[1.0, 0.9457796098355941, 1.0, 1.0], [0.9457796098355941, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9992557393942864], [1.0, 1.0, 0.9992557393942864, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivityMatrix, arrivalRates))
    runTest('iiGreedy2', [pattern], createTestFile, IIGreedyAlgorithm(IterativeImprovementType.CIRCLE_BASED), nasdaqEventStream)

def dpLdPatternSearchTest(createTestFile = False):
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
    selectivityMatrix = [[1.0, 0.9457796098355941, 1.0, 1.0], [0.9457796098355941, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9992557393942864], [1.0, 1.0, 0.9992557393942864, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivityMatrix, arrivalRates))
    runTest('dpLd1', [pattern], createTestFile, DynamicProgrammingLeftDeepAlgorithm(), nasdaqEventStream)

def dpBPatternSearchTest(createTestFile = False):
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
    selectivityMatrix = [[1.0, 0.9457796098355941, 1.0, 1.0], [0.9457796098355941, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9992557393942864], [1.0, 1.0, 0.9992557393942864, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivityMatrix, arrivalRates))
    runTest('dpB1', [pattern], createTestFile, DynamicProgrammingBushyAlgorithm(), nasdaqEventStream)

def zStreamOrdPatternSearchTest(createTestFile = False):
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
    selectivityMatrix = [[1.0, 0.9457796098355941, 1.0, 1.0], [0.9457796098355941, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9992557393942864], [1.0, 1.0, 0.9992557393942864, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivityMatrix, arrivalRates))
    runTest('zstream-ord1', [pattern], createTestFile, ZStreamOrdAlgorithm(), nasdaqEventStream)

def zStreamPatternSearchTest(createTestFile = False):
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
    selectivityMatrix = [[1.0, 0.9457796098355941, 1.0, 1.0], [0.9457796098355941, 1.0, 0.15989723367389616, 1.0], [1.0, 0.15989723367389616, 1.0, 0.9992557393942864], [1.0, 1.0, 0.9992557393942864, 1.0]]
    arrivalRates = [0.016597077244258872, 0.01454418928322895, 0.013917884481558803, 0.012421711899791231]
    pattern.setAdditionalStatistics(StatisticsTypes.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivityMatrix, arrivalRates))
    runTest('zstream1', [pattern], createTestFile, ZStreamAlgorithm(), nasdaqEventStream)

def frequencyTailoredPatternSearchTest(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("DRIV", "a"), QItem("MSFT", "b"), QItem("CBRL", "c")]),
        AndFormula(
            GreaterThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])),
            GreaterThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))
        ),
        timedelta.max
    )
    frequencyDict = {"MSFT": 256, "DRIV": 257, "CBRL": 1}
    pattern.setAdditionalStatistics(StatisticsTypes.FREQUENCY_DICT, frequencyDict)
    runTest('frequencyTailored1', [pattern], createTestFile, AscendingFrequencyAlgorithm(), nasdaqEventStream)

def nonFrequencyTailoredPatternSearchTest(createTestFile = False):
    pattern = Pattern(
        SeqOperator([QItem("DRIV", "a"), QItem("MSFT", "b"), QItem("CBRL", "c")]),
        AndFormula(
            GreaterThanFormula(IdentifierTerm("a", lambda x: x["Opening Price"]), IdentifierTerm("b", lambda x: x["Opening Price"])),
            GreaterThanFormula(IdentifierTerm("b", lambda x: x["Opening Price"]), IdentifierTerm("c", lambda x: x["Opening Price"]))
        ),
        timedelta.max
    )
    runTest('nonFrequencyTailored1', [pattern], createTestFile, TrivialAlgorithm(), nasdaqEventStream)

oneArgumentsearchTest()
simplePatternSearchTest()
googleAscendPatternSearchTest()
amazonInstablePatternSearchTest()
msftDrivRacePatternSearchTest()
googleIncreasePatternSearchTest()
amazonSpecificPatternSearchTest()
googleAmazonLowPatternSearchTest()
nonsensePatternSearchTest()
hierarchyPatternSearchTest()
nonFrequencyPatternSearchTest()
frequencyPatternSearchTest()
nonFrequencyPatternSearch2Test()
frequencyPatternSearch2Test()
nonFrequencyPatternSearch3Test()
frequencyPatternSearch3Test()
nonFrequencyPatternSearch4Test()
frequencyPatternSearch4Test()
nonFrequencyPatternSearch5Test()
frequencyPatternSearch5Test()
frequencyPatternSearch6Test()
greedyPatternSearchTest()
iiRandomPatternSearchTest()
iiRandom2PatternSearchTest()
iiGreedyPatternSearchTest()
iiGreedy2PatternSearchTest()
zStreamOrdPatternSearchTest()
zStreamPatternSearchTest()
dpBPatternSearchTest()
dpLdPatternSearchTest()
nonFrequencyTailoredPatternSearchTest()
frequencyTailoredPatternSearchTest()
