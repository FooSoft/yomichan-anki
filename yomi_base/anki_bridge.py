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
