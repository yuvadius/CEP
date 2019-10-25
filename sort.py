import re

def sortSecond(val): 
    return val[1]

with open("NASDAQ_20080201_1.txt", "r") as f:
    content = f.readlines()
for i in range(len(content)): 
    content[i] = (content[i], re.findall("(?<=\,)(.*?)(?=\,)", content[i])[0])

content.sort(key = sortSecond)
f2 = open("NASDAQ_20080201_1_sorted.txt", "a")
for i in range(len(content)): 
    f2.write(content[i][0])
f2.close()

print(content[341794])