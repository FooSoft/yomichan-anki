class Translator:
    def __init__(self, dictionary):
        self.dictionary = dictionary


    def findTerm(self, text, wildcards=False):
        results = []
        length = None
        for i in xrange(len(text), 0, -1):
            term = text[:i]
            for entry in self.dictionary.findTerm(term, wildcards):
                if length is None:
                    length = i
                results.append(entry)

        return results, length


    def findCharacters(self, text):
        results = []
        for i in xrange(len(text), 0, -1):
            term = text[:i]
            for entry in self.dictionary.findCharacter(root):
                results.append(entry)
        return results

    def processTerm(self, groups, source, rules=list(), root=str(), wildcards=False):
        root = root or source

        for entry in self.dictionary.findTerm(root, wildcards):
            key = entry['expression'], entry['traditional']
            if key not in groups:
                groups[key] = u'', source, rules
