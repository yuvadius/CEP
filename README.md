# CEP
A generic CEP library in python(requires python version 3.7+).

As Wikipedia states, Complex event processing, or CEP, is event processing that combines data from multiple sources to infer events or patterns that suggest more complicated circumstances.

CEP executes a set of algorithms which, as said, can infer events, patterns and sequences. The input of these algorithms are event streams and patterns, and the result of these calculations are pattern matches, or matches.

The algorithms are accessible for use with our API.

This short documentation will be updated regularly.

Github doc examples:

https://github.com/etingof/pysnmp

https://github.com/segmentio/nightmare

# Features
* [X] A mechanism for CEP pattern evaluation based on the acyclic graph model
* [X] Instance-based memory model (i.e., all partial results are explicitly stored in memory)
* [X] Trivial algorithm for graph construction (converting a list of events into a left-deep tree)
* [X] The pattern is provided as a Python class
* [X] Built-in dataset scheme
* [X] File-based input/output

# Download & Install
TBD

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

# Searching for pattern matches in the created input file
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

"""
This pattern is looking for an amazon stock in peak price of 73.
"""
amazonSpecificPattern = Pattern(
    SeqOperator([QItem("AMZN", "a")]),
    EqFormula(IdentifierTerm("a", lambda x: x["Peak Price"]), AtomicTerm(73))
)
cep = CEP(Tree, [amazonSpecificPattern], events)
fileOutput(cep.getPatternMatchStream(), 'amazonSpecificMatches.txt')
```

# API
#### The API defines the following interfaces: ####
* #### CEP ####
This class is the main Complex Event Processing Unit.

A CEP object is constructed with an algorithm, optional patterns and an optional event stream.
```
__init__(self, algorithm: Algorithm, patterns: List[Pattern] = None, events: Stream = None)
```

The CEP Object has the following functions:

```
addPattern(self, pattern: Pattern, priorityFactor: float = 0.5)
```
Adds a pattern to search matches for in the event stream. You can attach to the pattern an optional priority factor to prioritize that pattern when processing is heavy.

```
addEvent(self, event: Event)
```
Adds an event to the event stream.

```
getPatternMatch(self)
```
Returns the next pattern match found by the algorithm.

```
getPatternMatchStream(self)
```
Returns the output stream object of the CEP unit.


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
end(self)
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
This function receives a path to a file containing an Event Stream, and the column key names, as well as the key representing the event type. It returns a stream of event objects loaded from the file.

```
fileOutput(matches: Stream, fileOutputPath: str = 'matches.txt')
```
This function receives a stream of pattern matches and a file output path (default is 'matches.txt'), and writes the matches stream
to the file in the given file path.

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

*
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
  
*
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

*
  *
    * Term

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

* #### Algorithm ####
This class is an abstract class used to represent a CEP algorithm.
Every subclass of it which represents a concrete algorithm shall not be instantiated either, but to be sent to CEP objects as the algorithm parameter.

Every concrete algorithm subclass shall implement the following static function:
```
eval(pattern: Pattern, events: Stream, matches : Stream)
```
Receives a pattern and an event stream and performs the CEP with the algorithm it represents. It also receives a pattern matches stream
to write the output to.

The algorithms given in this API are:
* Tree - the acyclic graph model.
