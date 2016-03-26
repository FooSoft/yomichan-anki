import anki.sched
import math
import datetime
import random



class Scheduler(anki.sched.Scheduler):
    def __init__(self,col,filecache,scheduleVariationPercent = 0.0,minimumGain = 0.05,hideMinimumGain = False, weekDays = [True,True,True,True,True,True,True]):
        anki.sched.Scheduler.__init__(self,col)
        self.filecache = filecache
        self.scheduleVariationPercent = int(scheduleVariationPercent)
        # Any occuring vocabulary's ivl will increase by at least 5%
        self.minimumGain = minimumGain
        self.hideMinimumGain = hideMinimumGain
        self.weekDays = weekDays
        self.dueCache = dict()
        self.reset()
        
    def answerCard(self,card,ease):
        if ease == 1:
            for m, value in card.note().items():
                if m[:9] == u"ConnectTo":
                    model = self.col.models.byName(m[9:])
                    if model is None:
                        continue
                    key = model[u"flds"][0][u"name"]
                    cards = self.col.findCards(key + u':"' + value + u'" note:' + m[9:])
                    for connectedCardId in cards:
                        connectedCard = self.col.getCard(connectedCardId)
                        connectedCard.startTimer()
                        anki.sched.Scheduler.answerCard(self,connectedCard,ease)
        anki.sched.Scheduler.answerCard(self,card,ease)
        
    def earlyAnswerCard(self,card,ease,timeUsed=None):
        if card.queue < 0:
            card.queue = 0
        if timeUsed is None:
            card.startTimer()
        else:
            card.timerStarted = time.time() - timeUsed
        self.answerCard(card,ease)
    
    def _updateRevIvl(self, card, ease):
        idealIvl = self._nextRevIvl(card, ease)
        adjIv1 = self._adjRevIvl(card, idealIvl)
        if card.queue == 2:
            card.ivl = card.ivl + math.ceil(self._smoothedIvl(card)*(adjIv1 - card.ivl))
        else:
            card.ivl = adjIvl
        card.ivl = random.randint(int(card.ivl * (1-self.scheduleVariationPercent/100.0)),int(card.ivl * (1+self.scheduleVariationPercent/100)))
        counter = 0
        while counter < 4 and not self.weekDays[(datetime.date.today() + datetime.timedelta(card.ivl)).weekday()] and card.ivl > 1:
            card.ivl += random.randint(0,1) * 2 - 1
            counter = counter + 1
            
    def _smoothedIvl(self,card):
        if card.ivl > 0 and card.queue == 2:
            return max(self.minimumGain,float(card.ivl - self._daysEarly(card))/card.ivl)
        else:
            return 1
        
    def _daysEarly(self, card):
        "Number of days earlier than scheduled."
        due = card.odue if card.odid else card.due
        return max(0, due - self.today)
        
    def deckDueList(self):
        filecache = self.filecache()
        yomichanDeck = self.col.decks.byName(u'Yomichan')
        data = anki.sched.Scheduler.deckDueList(self)
        if yomichanDeck is not None:
            for deck in filecache:
                id = self.col.decks.id(deck)
                if filecache[deck] is None:
                    due = 0
                    new = 0
                elif self.hideMinimumGain:
                    due = int(filecache[deck].dueness - filecache[deck].foundvocabs * self.minimumGain)
                    new = len(filecache[deck].wordsNotFound)
                else:
                    due = int(filecache[deck].dueness)
                    new = len(filecache[deck].wordsNotFound)
                data.append([deck, id, due, 0, new])
                self.dueCache[deck] = due
        return data
