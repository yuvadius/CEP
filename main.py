from CEP import *

p1 = CEP(Event.fileInput("NASDAQ_20080201_1_sorted.txt"))
thread = p1.findPattern(0, 0, True)
x = Tree()