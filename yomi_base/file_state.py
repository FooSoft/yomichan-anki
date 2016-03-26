import reader_util
import time



class FileState:
    def __init__(self,fn,stripReadings,languages=[]):
        self.alias = dict()
        self.languages = languages
        self.wordsAll = dict()
        self.wordsBad = dict()
        self.wordsMarkup = dict()
        self.sep = u"\U00012000"
        self.lineBreak = u"\U00012001"
        self.wordsNotFound = []
        self.dueness = 0.0
        self.wrong = 0
        self.correct = 0
        self.resetTimer()
        self.stripReadings = stripReadings
        if fn is None:
            self.filename = u''
        else:
            self.filename = unicode(fn)
            self.load()
    
    def load(self):
        with open(self.filename) as fp:
            self.content = fp.read()

        self.content, self.encoding = reader_util.decodeContent(self.content)
        if self.stripReadings:
            self.content = reader_util.stripReadings(self.content)
    

    def resetTimer(self):
        self.timerStarted = time.time()
    
            
    def getPlainVocabularyList(self):
        return  u'### VOCABULARY IN THIS TEXT ###\n'+u'\n'.join(self.wordsAll.keys())+u'\n'.join(self.wordsNotFound) 

    def getExportVocabularyList(self,allowedTags):
        def access(x,y):
            if y not in x:
                return u''
            else:
                return x[y]
        #don't export filename, because it's unnecessary for importing
        if 'filename' in allowedTags:
            allowedTags.remove('filename')
        vocabularyDefinitions = [self.sep.join([x]+([access(self.wordsMarkup[x],y).replace(u'\n',self.lineBreak) for y in allowedTags])) for x in self.wordsAll.keys()]
        return  u'### VOCABULARY IN THIS TEXT (EXPORT)###\n'+ self.sep.join(allowedTags) +u'\n'+ u'\n'.join(vocabularyDefinitions)+u'\n'.join(self.wordsNotFound) 
    
    def getAliasList(self):
        if not self.alias.items():
            return u''
        else:
            return u'### ALIAS ###\n' + u'\n'.join([eng + self.sep + jpn for eng,jpn in self.alias.items()]) + u'\n'
    
    def overwriteVocabulary(self,value,card):
        self.wordsAll[value] = card
        if value in self.wordsBad:
            self.wordsBad[value] = card
    
    
    def addVocabulary(self,value,card,addToBadListToo = True):
        self.wordsAll[value] = card
        if addToBadListToo:
            self.wordsBad[value] = card             
    
    def addMarkup(self,value,markup):
        self.wordsMarkup[value] = markup
        
    def findVocabulary(self,sched,allCards,needContent=True):
        lines = self.content.splitlines()
        state = "text"
        self.exportedVocab = False
        exportedTags = None
        self.content = u''
        self.dueness = 0.0
        self.foundvocabs = 0
        self.wordsNotFound = []
        shuffle = False
        filteredLines = []
        for line in lines:
            if self.exportedVocab and not exportedTags and state == "vocabulary":
                exportedTags = line.split(self.sep)
            elif line == u'### SHUFFLE THIS TEXT ###':
                shuffle = True
            elif line == u'### ALIAS ###':
                state = "alias"
            elif line == u'### MECAB ###':
                state = "mecab"
            elif line == u'### VOCABULARY IN THIS TEXT ###':
                state = "vocabulary"
            elif line == u'### VOCABULARY IN THIS TEXT (EXPORT)###':
                state = "vocabulary"
                self.exportedVocab = True
            elif state == "mecab":
                self.exportedVocab = True
                definitions = line.split(self.sep)
                line = definitions.pop(0)
                markup = dict()
                markup['summary'] = line
                markup['expression'] = definitions[0]
                markup['reading'] = definitions[1]
                markup['kanji'] = u""
                markup['hanja'] = u""
                if "japanese" in self.languages:
                    definition = self.languages["japanese"].dictionary.findTerm(word=definitions[0],reading=definitions[1])
                    if len(definition)>0:
                        markup['glossary'] = definition[0]['glossary']
                    else:
                        markup['glossary'] = u""
                markup['line'] = definitions[2]
                markup['sentence'] = definitions[3]
                markup['traditional'] = u""
                markup['language'] = u"Japanese"
                markup['filename'] = self.filename
                self.wordsMarkup[line] = markup
                if line in allCards:
                    card = allCards[line]
                    self.dueness += sched._smoothedIvl(card)
                    self.wordsAll[line] = card
                    self.foundvocabs += 1
                else:
                    self.wordsNotFound.append(line)
            elif state == "vocabulary":
                if self.exportedVocab:
                    definitions = line.split(self.sep)
                    line = definitions.pop(0)
                    markup = dict()
                    for i, field in enumerate(definitions):
                        if i>= len(exportedTags):
                            break
                        markup[exportedTags[i]] = field.replace(self.lineBreak,u'\n')
                    markup['filename'] = self.filename
                    self.wordsMarkup[line] = markup
                if line in allCards:
                    card = allCards[line]
                    self.dueness += sched._smoothedIvl(card)
                    self.wordsAll[line] = card
                    self.foundvocabs += 1
                else:
                    self.wordsNotFound.append(line)
            elif state == "alias":
                eng,jpn = line.split(self.sep)
                self.alias[eng] = jpn
            elif needContent:
                filteredLines.append(line)
        if shuffle:
            import random
            random.shuffle(filteredLines)
            filteredLines.append(u'### SHUFFLE THIS TEXT ###')
        self.content = u'\n'.join(filteredLines) + u'\n'
        
    def onLearnVocabularyList(self,sched):
        self.correct = 0
        self.wrong = 0
        self.timeTotal = time.time() - self.timerStarted
        self.timePerWord = self.timeTotal / len(self.wordsAll)
        for word in self.wordsAll:
            if word in self.wordsBad:
                sched.earlyAnswerCard(self.wordsBad[word],1,self.timePerWord)
                self.wrong += 1
            else:
                sched.earlyAnswerCard(self.wordsAll[word],3,self.timePerWord)
                self.correct += 1
