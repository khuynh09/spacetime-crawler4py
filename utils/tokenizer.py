import re
import sys

# Runtime Complexity: This code will run in polynomial-time
# and scale relative to the size of the file(number of words)
# with the worst case being O(nlogn) because of Python's sorted function


class Tokenizer:
    def __init__(self, fileName):
        self.fileName = fileName
        self.tokenList = []
        self.tokenFreq = {}
        with open(self.fileName, 'r', encoding='utf8') as openedFile:
            for line in openedFile:
                tokens = re.sub(r'[^\w\s]|_', '', line).rstrip(
                    '\r\n').rstrip().split(" ")
                i = 0
                while i < len(tokens):
                    tokens[i] = tokens[i].lower()
                    i += 1
                self.tokenList.extend(tokens)

    def tokenize(self):
        return self.tokenList

    def computeWordFrequencies(self):
        for token in self.tokenList:
            if (token in self.tokenFreq):
                self.tokenFreq[token] += 1
            else:
                self.tokenFreq[token] = 1
        return self.tokenFreq

    def __print__(self):
        sortedDict = dict(sorted(self.tokenFreq.items(),
                          key=lambda x: x[1], reverse=True))
        for item in sortedDict.items():
            print(item[0], "=", item[1])


if __name__ == '__main__':
    tokenizer = Tokenizer(sys.argv[1])
    tokenizer.computeWordFrequencies()
    tokenizer.__print__()
