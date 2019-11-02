# CEP
A generic CEP library in python(requires python version 3.7+).

As Wikipedia states, Complex event processing, or CEP, is event processing that combines data from multiple sources to infer events or patterns that suggest more complicated circumstances.

CEP executes a set of algorithms which, as said, can infer events, patterns and sequences. The input of these algorithms are events and queries, and the result of these calculations are patterns.

The algorithms are exposed with an API, so you can add or remove algorithms freely.

This short documentation will be updated regularly.

Github doc examples:

https://github.com/etingof/pysnmp

https://github.com/segmentio/nightmare

# Features
* [ ] A mechanism for CEP pattern evaluation based on the acyclic graph model
* [ ] AND/SEQ operators with arbitrary Boolean conditions of two operands each (event1.attr1 </>/==/!= event2.attr2)
* [X] Instance-based memory model (i.e., all partial results are explicitly stored in memory)
* [X] Trivial algorithm for graph construction (converting a list of events into a left-deep tree)
* [X] The pattern is provided as a Python class
* [ ] Built-in dataset scheme
* [X] File-based input/output

# Download & Install
TBD

# Examples
The following example creates a strict sequence query for an Apple stock change event followed by an Amazon stock change event followed by an Avid stock change event, then query is applied on the event stream in a NASDAQ stock changes file. 
```
events = Event.fileInput("NASDAQ_20080201_1_sorted.txt", 0)  # Create an event stream from a file

query = Query(
StrictSequencePatternStructure([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("AVID", "c")])
)  # define a query

cep = CEP(events)  # create a complex event processing object
cep.findPattern(query, Tree, False)  
# apply the query on the CEP object and get the results in file patterns.txt.
```

# API
#### The API defines the following interfaces: ####
* #### CEP ####
This class is the main Complex Event Processing Unit.

A CEP object is constructed with an Event Stream, practically a list of events, as following:
```
__init__(self, events: List[Event])
```

and has the following function:
```
findPattern(self, query: Query, algorithm: Algorithm, isThread: bool = False)
```
This function receives a Query object and an Algorithm class and performs a CEP according to the given query using the given algorithm. The Algorithm and Query classes are described below.
It also has a configuration parameter which allows the user to run the calculation on a background thread instead of blocking the main thread.

* #### Event ####
This class is used to represent a single Event. It is constructed with a list of fields and the Event type as following:
```
__init__(self, event: List, eventType: str)
```

The Event class has the following static function:
```
fileInput(filePath: str, eventTypeIndex: int) -> List[Event]
```
This function receives a path to a file containing an Event Stream. It also receives the index of the field which represents the event type, in order to match a type for each event. It returns a list of event objects representing the event stream loaded from the file.

* #### Query ####
This class is used to represent a query for a CEP object.
It is constructed with a PatternStructure object, an optional conditional Formula object (where clause), and an optional sliding window timedelta object (within clause):
```
__init__(self, 
          patternStructure: PatternStructure, 
          patternMatchingCondition: Formula = TrueFormula(), 
          slidingWindow: timedelta = timedelta.max)
```
The PatternStructure, Formula and timedelta classes are described below.

*
  * #### PatternStructure ####
This class is an abstract class used to represent a pattern structure, i.e. a PATTERN clause's argument.

Every instantiable subclass of this class can be used as a pattern structure. It shall be constructed with a list of QItem objects:
```
__init__(self, qitems: List[QItem])
```

QItem class is a class used to represent a single "argument" in the PATTERN clause, i.e. a type-name binding in the sequence specification. The QItem class is described below.

The PatternStructure's subclasses represent the type of pattern structure used, e.g. StrictSequencePatternStructure.

The following classes inherit from PatternStructure:
  * StrictSequencePatternStructure
  * More classes TBD

Every one of the classes represent a different pattern structure specification.

*
  *
    * #### QItem ####
The QItem class is merely a set of fields representing a defined name in the pattern structure, and the name shall be defined with a certain type, can be specified as a negated pattern member, and can be defined as a "one or more" list of events of a certain type, formally called "kleene plus". It is constructed as following:
```
__init__(self, eventType: str, name: str, kleenePlus: bool = False, negated: bool = False)
```

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
  * `TrueFormula()`

Represents the formula `True`.

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

* #### Algorithm ####
This class is an abstract class used to represent a CEP algorithm.
Every subclass of it which represents a concrete algorithm shall not be instantiated either, but to be sent to CEP objects as the algorithm parameter. It is practically a singleton class.

The Algorithm abstract class provides the following static method:
```
fileOutput(patterns: List[Pattern])
```
Which receives a list of patterns and prints them into a file named pattern.txt.

Every concrete algorithm subclass shall implement the following static function:
```
eval(query: Query, events: List[Event])
```
Receives a query and an event stream and performs the CEP with the algorithm it represents.

* #### Pattern ####
This class is used to represent a pattern found by a CEP. It is constructed with a list of events, which are the events that matched     the pattern, and an optional time field to save the time it took to find this pattern since the start of the process in milliseconds.
The constructor is defined as following:
```
__init__(self, events: List[Event], time: int = -1)
```
The value (-1) is considered as an undefiened time period.
