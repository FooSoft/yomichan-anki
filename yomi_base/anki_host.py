# -*- coding: utf-8 -*-

# Copyright (C) 2011  Alex Yatskov
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


import aqt
import re


class Anki:
    def addNote(self, deckName, modelName, fields, tags=unicode()):
        note = self.createNote(fields, deckName, modelName, tags)
        if not note:
            return None

        self.collection().addNote(note)
        self.window().requireReset()

        return note.id


    def canAddNote(self, fields):
        return bool(self.createNote(fields))


    def createNote(self, deckName, modelName, fields, tags=unicode()):
        deck = self.findDeck(deckName)
        if deck is None:
            return None

        model = self.findModel(modelName)
        if model is None:
            return None

        note = self.collection().newNote()
        note.tags = re.split('[;,\s]', tags)
        note.model()['did'] = deck['id']

        for name, value in fields.items():
            note[name] = value

        return None if note.dumpOrEmpty() else note


    def setCurrentModel(self, modelName):
        #m = self.deck.models.byName(ret.name)
        #self.deck.conf['curModel'] = m['id']
        #cdeck = self.deck.decks.current()
        #cdeck['mid'] = m['id']
        #self.deck.decks.save(cdeck)
        #runHook("currentModelChanged")
        #self.mw.reset()
        pass


    def setCurrentDeck(self, deckName):
        pass


    #def browseNote(self, noteId):
        #browser = ui.dialogs.get('CardList', self.window())
        #browser.dialog.filterEdit.setText('fid:' + str(noteId))
        #browser.updateSearch()
        #browser.onnote()


    def window(self):
        return aqt.mw


    def form(self):
        return self.window().form


    def toolsMenu(self):
        return self.form().menuTools


    def collection(self):
        return self.window().col


    def models(self):
        return self.collection().models


    def modelNames(self):
        return self.models().allNames()


    def modelFieldNames(self, model):
        return [field['name'] for field in model['flds']]


    def findModel(self, name):
        return self.models().byName(name)


    def currentModel(self):
        return self.models().current()


    def decks(self):
        return self.collection().decks


    def deckNames(self):
        return self.decks().allNames()


    def findDeck(self, name):
        return self.decks().byName(name)


    def currentDeck(self):
        return self.decks().current()

