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
import anki.hooks


class Anki:
    def addNote(self, deckName, modelName, fields, tags=list()):
        note = self.createNote(fields, deckName, modelName, tags)
        if note is not None:
            self.collection().addNote(note)
            self.decks().save(self.currentDeck())
            self.window().requireReset()


    def canAddNote(self, deckName, modelName, fields):
        return bool(self.createNote(deckName, modelName, fields))


    def createNote(self, deckName, modelName, fields, tags=list()):
        model = self.findModel(modelName)
        if model is None:
            return None

        deck = self.findDeck(deckName)
        if deck is None:
            return None

        #~ conf = self.collection().conf
        #~ deck = self.currentDeck()
        #~ if conf['curModel'] != model['id'] or deck['mid'] != model['id']:
            #~ conf['curModel'] = deck['mid'] = model['id']
            #~ self.collection().decks.save(deck)
            #~ anki.hooks.runHook('currentModelChanged')
            #~ self.window().reset()

        #~ self.collection().conf['curModel'] = model['id']
        #~ deck['mid'] = model['id']

        note = anki.notes.Note(self.collection(), model)
        note.model()['did'] = deck['id']
        note.tags = tags

        for name, value in fields.items():
            note[name] = value

        return None if note.dupeOrEmpty() else note


    #~ def browseNote(self, noteId):
        #~ browser = ui.dialogs.get('CardList', self.window())
        #~ browser.dialog.filterEdit.setText('fid:' + str(noteId))
        #~ browser.updateSearch()
        #~ browser.onnote()


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

