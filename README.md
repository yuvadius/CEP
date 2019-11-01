# CEP
A generic CEP library in python.

As Wikipedia states, Complex event processing, or CEP, is event processing that combines data from multiple sources to infer events or patterns that suggest more complicated circumstances.

CEP executes a set of algorithms which, as said, can infer events, patterns and sequences. The input of these algorithms are events and queries, and the result of these calculations are patterns.

The algorithms are exposed with an API, so you can add or remove algorithms freely.

This short documentation will be updated regularly.

Github doc examples:

https://github.com/etingof/pysnmp

https://github.com/segmentio/nightmare

# Features
* [~] A mechanism for CEP pattern evaluation based on the acyclic graph model
* [ ] AND/SEQ operators with arbitrary Boolean conditions of two operands each (event1.attr1 </>/==/!= event2.attr2)
* [X] Instance-based memory model (i.e., all partial results are explicitly stored in memory)
* [X] Trivial algorithm for graph construction (converting a list of events into a left-deep tree)
* [X] The pattern is provided as a Python class
* [ ] Built-in dataset scheme
* [X] File-based input/output

# Download & Install
TBD

# Examples
The following example creates a strict sequence query for an Apple stock change event followed by an
Amazon stock change event followed by an Avid stock change event, then query is applied on the event stream
in a NASDAQ stock changes file. 
`
events = Event.fileInput("NASDAQ_20080201_1_sorted.txt", 0)  # Create an event stream from a file

query = Query(
StrictSequencePatternStructure([QItem("AAPL", "a"), QItem("AMZN", "b"), QItem("AVID", "c")])
)  # define a query

cep = CEP(events)  # create a complex event processing object
cep.findPattern(query, Tree, False)  # apply the query on the CEP object and get the results in file patterns.txt.
`

# API
#### The API defines the following classes: ####
<details>
    <summary>CEP</summary>
    <p></p>
</details>
<details>
    <summary>Event</summary>
    <p></p>
</details>
<details>
    <summary>Query</summary>
    <p></p>
    <details>
        <summary>Formula</summary>
        <p></p>
    </details>
    <details>
        <summary>PatternStructure</summary>
        <p></p>
            <details>
            <summary>QItem</summary>
            <p></p>
        </details>
    </details>
    <details>
        <summary>datetime.timedelta</summary>
        <p></p>
    </details>
</details>
<details>
    <summary>Pattern</summary>
    <p></p>
</details>
