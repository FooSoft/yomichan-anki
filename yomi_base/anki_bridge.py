# -*- coding: utf-8 -*-

# Copyright (C) 2013  Alex Yatskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import anki
import aqt

from anki.sched import Scheduler
import time

class EarlyScheduler(Scheduler):
    def __init__(self,col,filecache):
        Scheduler.__init__(self,col)
        self.filecache = filecache
        self.reset()
        
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
            card.ivl = card.ivl + int(max(0,self._smoothedIvl(card))*(adjIv1 - card.ivl))
        else:
            card.ivl = adjIvl
    
    def _smoothedIvl(self,card):
        if card.ivl > 0 and card.queue == 2:
            return (card.ivl - self._daysEarly(card))/card.ivl
        else:
            return 1
        
    def _daysEarly(self, card):
        "Number of days earlier than scheduled."
        due = card.odue if card.odid else card.due
        return max(0, due - self.today)
        
    def deckDueList(self):
        filecache = self.filecache()
        yomichanDeck = self.col.decks.byName(u'Yomichan')
        data = Scheduler.deckDueList(self)
        if yomichanDeck is not None:
            for deck in filecache:
                id = self.col.decks.id(deck)
                if filecache[deck] is None:
                    data.append([deck, id, 0, 0, 0])
                else:
                    data.append([deck, id, int(filecache[deck].dueness), 0, 0])
            for name,id in self.col.decks.children(yomichanDeck['id']):
                if name not in filecache and self.col.decks.get(id)['id']!=1:
                    self.col.decks.rem(id)
        return data


class Anki:
    def addNote(self, deckName, modelName, fields, tags=list()):
        note = self.createNote(deckName, modelName, fields, tags)
        if note is not None:
            collection = self.collection()
            collection.addNote(note)
            collection.autosave()
            self.startEditing()
            return note.id


    def canAddNote(self, deckName, modelName, fields):
        return bool(self.createNote(deckName, modelName, fields))


    def createNote(self, deckName, modelName, fields, tags=list()):
        model = self.models().byName(modelName)
        if model is None:
            return None

        deck = self.decks().byName(deckName)
        if deck is None:
            return None

        note = anki.notes.Note(self.collection(), model)
        note.model()['did'] = deck['id']
        note.tags = tags

        for name, value in fields.items():
            if name in note:
                note[name] = value

        if not note.dupeOrEmpty():
            return note


    def browseNote(self, noteId):
        browser = aqt.dialogs.open('Browser', self.window())
        browser.form.searchEdit.lineEdit().setText('nid:{0}'.format(noteId))
        browser.onSearch()
        
    
    def getNotes(self, modelName, key, value):
        return self.collection().findNotes(key + u':' + value + u' note:' + modelName)
        
        
    def getCards(self, modelName, onlyFirst = False):
        model = self.models().byName(modelName)
        modelid = model[u"id"]
        query = "select " + ("min(c.id)" if onlyFirst else "c.id")
        query+= ",n.sfld,n.id from cards c "
        query+= "join notes n on (c.nid = n.id) " 
        query+= "where n.mid=%d" % (modelid)
        if onlyFirst: query+= "group by n.id"
        return self.collection().db.execute(query)
        
    
    def getCardsByNote(self, modelName, key, value):
        return self.collection().findCards(key + u':' + value + u' note:' + modelName)
    
    
    def getModelKey(self, modelName):
        model = self.collection().models.byName(modelName)
        if model is None:
            return None
        frstfld = model[u"flds"][0]
        return frstfld[u"name"]
        

    def startEditing(self):
        self.window().requireReset()


    def stopEditing(self):
        if self.collection():
            self.window().maybeReset()


    def window(self):
        return aqt.mw


    def addUiAction(self, action):
        self.window().form.menuTools.addAction(action)


    def collection(self):
        return self.window().col


    def models(self):
        return self.collection().models


    def modelNames(self):
        return self.models().allNames()


    def modelFieldNames(self, modelName):
        model = self.models().byName(modelName)
        if model is not None:
            return [field['name'] for field in model['flds']]


    def decks(self):
        return self.collection().decks


    def deckNames(self):
        return self.decks().allNames()
