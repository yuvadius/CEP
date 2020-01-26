# CEP
A generic CEP library in python(requires python version 3.7+).

As Wikipedia states, Complex event processing, or CEP, is event processing that combines data from multiple sources to infer events or patterns that suggest more complicated circumstances.

CEP executes a set of algorithms which, as said, can infer events, patterns and sequences. The input of these algorithms are event streams and patterns, and the result of these calculations are pattern matches, or matches.

The algorithms are accessible for use with our API.

This short documentation will be updated regularly.

# Features
* [X] A mechanism for CEP pattern evaluation based on the acyclic graph model
* [X] Instance-based memory model (i.e., all partial results are explicitly stored in memory)
* [X] The pattern is provided as a Python class
* [X] Several algorithms for constructing the CEP graph
* [X] Generic dataset schema
* [X] Generic input/output interface (With support for File-based input/output)

# How to Use
* The root of this library is the CEP object. The CEP object is used to perform complex event processing on an event stream.
* The CEP object consists of a processing algorithm, event stream, patterns, and matches container. It runs its algorithm on separate threads to find matches for the given patterns. The matches are found in the event stream. The event stream can be given on construction, and you may add events on the fly - either through the given event stream or with the CEP object.
* To create an event stream you can manually create an empty stream and add events to it, and you can also provide a csv file to the fileInput function.
* To handle the CEP output you can manually read the events from the CEP object or from the matches container, or use the fileOutput function to print the matches into a file.
* To create a pattern, you can construct a pattern structure - SEQ(A, B, C) or AND(X, Y).
    * You can attach a formula that the atomic items in the pattern structure can suffice.
    * You can attach a time delta in which the atomic items in the pattern structure should appear in the stream.

# Program Flow
* Every pattern of a CEP thread runs on a different thread.
* Every thread runs an algorithm's evaluation function.
* The CEP algorithms implemented in this library are based on the acyclic graph model. They will create the acyclic graph for the pattern and start looking for matches in the event stream.
* Upon a partial match, it shall be stored in memory.
* Upon a match, the algorithm will add that match to a given container.

# Optimization Notes
* Formulas can affect memory usage. The algorithm splits the formula to parts which are relevant to partial results. When partial results are stored in memory, they may be irrelevant according to the formula, but the algorithm can't know that yet. For instance, SEQ(A, B, C) where A > B + C. When storing a partial result of A, B - if B >= A then the partial result can be deleted, but the algorithm can only know that when a C appears. If the formula was A > B and A > B + C, the algorithm would have split the "and" and would have known that it can dump the partial result.

# Examples

```
# Creating an event stream from a file, and giving the column format and the key as parameters.
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

# Searching for pattern matches in the created input stream
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

googleAscendPatternSearchTest(True) # Use True to create a test
googleAmazonLowPatternSearchTest() # If the test exists then don't send arguments
# Check tests.py for more examples
```

# API
#### The API defines the following interfaces: ####
* #### CEP ####
This class is the main Complex Event Processing Unit.

A CEP object is constructed with an algorithm, optional patterns an optional event stream, optional output container, and a config parameter to whether save a copy with the history of the event stream and replay it on new patterns - saveReplica and also
performanceSpecs of type PerformanceSpecifications that will help in building the tree.
```
def __init__(self, algorithm: EvaluationMechanism, patterns: List[Pattern] = None, events: Stream = None, output: Container = None, saveReplica: bool = True, performanceSpecs : PerformanceSpecifications = None):
```

The CEP Object has the following functions:

```
addPattern(self, pattern: Pattern, priority: int = 0)
```
Adds a pattern to search matches for in the event stream. You can attach to the pattern an optional priority value to the pattern to prioritize that pattern when processing is heavy.

```
addEvent(self, event: Event)
```
Adds an event to the event stream.

```
getPatternMatch(self)
```
Returns the next pattern match found by the algorithm.

```
getPatternMatchContainer(self)
```
Returns the output container object of the CEP unit.

```
close(self)
```
Closes the input event stream.

* #### Container ####
A class describing a container of objects.
Has the following abstract functions:
*
  * ```addItem(self, item)```
  * ```getItem(self)```
  * ```close(self)```

* #### Stream ####
A class describing stream objects which its functionality is similar to a queue. It is used to represent an event stream and a match stream. It is thread-safe.
It has the following functions:

```
__init__()
```
A constructor with no parameters.

```
addItem(self, item)
```
Adds the given item to the data stream.

```
getItem(self)
```
Returns the next item in the stream.

```
close(self)
```
Closes the data stream.

The stream is also iterable with a simple "for item in stream" loop, 
or using the ```__iter__()``` and ```__next__()``` functions it implements explicitly.

* #### IOUtils ####
This module is a set of functions which can be useful for handling I/O objects such as streams and events and provide an interface
for reading files as event streams and writing event streams to files.
It provides the following functions:

```
fileInput(filePath: str, keyMap: List, eventTypeKey: str, eventTimeKey: str) -> Stream
```
This function receives a path to a file containing an Event Stream, and the column key names, as well as the key representing the event type and the key representing the event timestamp. It returns a stream of event objects loaded from the file.

```
fileOutput(matches: Container, fileOutputPath: str = 'matches.txt')
```
This function receives a container of pattern matches and a file output path (default is 'matches.txt'), and writes the matches container to the file in the given file path.

* #### Event ####
This class is used to represent a single Event. It is constructed with a list of fields, the Event type and a timestamp as following:
```
__init__(self, event: List, eventType: str, date: datetime)
```

* #### Pattern ####
This class is used to represent a pattern for a CEP object.
It is constructed with a PatternStructure object, an optional conditional Formula object (where clause), and an optional sliding window timedelta object (within clause):
```
__init__(self, 
          patternStructure: PatternStructure, 
          patternMatchingCondition: Formula = None, 
          slidingWindow: timedelta = timedelta.max)
```
The PatternStructure, Formula and timedelta classes are described below.

* #### PatternStructure ####
This class is an abstract class used to represent a pattern structure, i.e. a PATTERN clause's argument.
The pattern can be nested, and can be composed of operators like SEQ, AND, ~ (negation) and ()* (kleene plus).

Every instantiable subclass of this class can be used as a pattern structure.
The pattern structure abstract class implements the following function:
```
getTopOperator(self) -> class
```
Returns the class of the top opreator in the pattern structure.

QItem class is a class used to represent an atomic "argument" in the PATTERN clause, i.e. a type-name binding in the sequence specification. The QItem class is described below.

The PatternStructure's subclasses represent the type of pattern structure used.

The following classes inherit from PatternStructure:
  * SeqOperator
  * AndOperator
  * NegationOperator
  * KleenePlusOperator
  * StrictSeqOperator
  
* #### Formula ####
This class is an abstract class which represents a logic formula with identifiers and values (a SASE+ formula) and can be               implemented by many formula classes which all shall implement the following function:
```
eval(self, binding: dict = {})
```
This function receives a name-value binding as a dictionary and evaluates to the value of the formula (True/False) when the values of the names are as bound. If there is a missing binding, it shall assume the optimistic case, in which the missing value shall not prevent the formula from evaluating to True.

Formulas are constructed with terms or other formulas.
The term abstract class is used to represent expressions and is described below.

The following classes inherit from Formula, presented with their constructors:
  * `AtomicFormula(leftTerm, rightTerm, relBinOp)`

Represents the formula `leftTerm relBinOp rightTerm`. 
RelBInOp is a Binary Operator such as `==`. It is an (x, y)->bool function.
  * `EqFormula(leftTerm, rightTerm)`

Represents the formula `leftTerm == rightTerm`.
  * `NotEqFormula(leftTerm, rightTerm)`

Represents the formula `leftTerm != rightTerm`.
  * `GreaterThanFormula(leftTerm, rightTerm)`

Represents the formula `leftTerm > rightTerm`.
  * `SmallerThanFormula(leftTerm, rightTerm)`

Represents the formula `leftTerm < rightTerm`.
  * `GreaterThanEqFormula(leftTerm, rightTerm)`

Represents the formula `leftTerm >= rightTerm`.
  * `SmallerThanEqFormula(leftTerm, rightTerm)`

Represents the formula `leftTerm <= rightTerm`.
  * `BinaryLogicOpFormula(leftFormula, rightFormula, binaryLogicOp)`

Represents the formula `leftFormula binaryLogicOp rightFormula`. 
RelBInOp is a Logic Operator such as `OR`, `AND`. It is a (bool, bool)->bool function.
  * `AndFormula(leftFormula, rightFormula)`

Represents the formula `leftFormula AND rightFormula`.

Every one of these classes represent a concrete formula, given their constructor parameters.

* #### Term ####

The Term abstract class is used to represent an expression. Every instantiable class of it represents a concrete expression which can be evaluated given a proper name-binding. It has the following function:
```
eval(self, binding: dict = {})
```
Evaluates to the term's value. 
If there are variables (identifiers) in the term, a name-value binding shall be inputted.

Term has the following subclasses, presented with their constructors:
* AtomicTerm(value)

Represents the term `value`.
* IdentifierTerm(name: str, getAttrFunc)

Represents the term `name.attr`.
It will use the getAttrFunc function to extract the value of the term from a name binding, i.e. `getAttrFunc(binding[name])`.
* BinaryOperationTerm(lhs, rhs, binOp)

Represents the term `lhs binOp rhs`.
BinOp is a binary operator such as +, -, *, /. It is an (x,y)->z function.
In the BinaryOperationTerm class and in all following classes, rhs and lhs are both terms.
* PlusTerm(lhs, rhs)

Represents the term `lhs + rhs`.
* MinusTerm(lhs, rhs)

Represents the term `lhs - rhs`.
* MulTerm(lhs, rhs)

Represents the term `lhs * rhs`.
* DivTerm(lhs, rhs)

Represents the term `lhs / rhs`.

All classes above represent a concrete term and can, given a proper name binding, evaluate the term they represent.

* #### datetime.timedelta ####
This class is used to represent a sliding window of a query (a WITHIN clause's argument).
It is an object used to represent a peroid of time and is described extensively in Python's documentation.

* #### Pattern Match ####
A class to represent a pattern match. Has the following constructor. It is used in pattern match streams.
```__init__(self, events: List[Event])```

* #### TreeAlgorithm ####
This class is an abstract class used to represent a CEP acyclic graph algorithm.
Every subclass of it which represents a concrete algorithm shall not be instantiated either, but to be sent to CEP objects as the algorithm parameter.

Every concrete tree based algorithm subclass shall implement the following function:
```
eval(pattern: Pattern, events: Stream, matches : Container, treeBluePrint)
```
Receives a pattern and an event stream and performs the CEP with the algorithm it represents. It also receives a pattern matches container to write the output to.

The tree construction algorithms supported in this API:
* Trivial Algorithm
Requires no statistics.
* Ascending Frequency Algorithm

Requires a frequency dictionary or arrival rates.
All following algorithms require selectivity matrix and arrival rates.
* Greedy Algorithm
* IIGreedy Algorithm (Iterative improvement based on greedy order).
* IIRandom Algorithm (Iterative improvement based on a random order).
* Utilization of Dynamic Programming for constructing an optimal left deep tree.
* Utilization of Dynamic Programming for constructing an optimal tree, not limited to a left deep topolgy.
* ZStream based construction Algorithm.
* Zstream-ord - Zstream such that the base order is a greedy order, and not a trivial one.

Some of the above algorithms require configuration and statistics.
The following statistics can be added to a pattern using pattern.setAdditionalStatistics:

*`pattern.setAdditionalStatistics(AdditionalStatisticsType.FREQUENCY_DICT, frequencyDict)`
*`pattern.setAdditionalStatistics(AdditionalStatisticsType.SELECTIVITY_MATRIX_AND_ARRIVAL_RATES, (selectivityMatrix, arrivalRates))`
*`pattern.setAdditionalStatistics(AdditionalStatisticsType.ARRIVAL_RATES, arrivalRates)`

The next chapter explains how statistics can be calculated.

* ### Statistics ###

In the file Statistics.py, there are several functions in order to calculate statistics.
All receive a pattern and a stream and return the required statistics.

`getOccurencesDict(pattern : Pattern, stream : Stream) -> frequencyDict`

`getSelectivityMatrix(pattern : Pattern, stream : Stream) -> selectivityMatrix`

`getArrivalRates(pattern : Pattern, stream : Stream) -> arrivalRates`
