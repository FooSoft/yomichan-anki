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
    def addNote(self, deckName, modelName, fields, tags=[]):
        collection = self.collection()
        if collection is None:
            return

        note = self.createNote(deckName, modelName, fields, tags)
        if note is None:
            return

        self.startEditing()

        collection.addNote(note)
        collection.autosave()

        return note.id


    def canAddNote(self, deckName, modelName, fields):
        return bool(self.createNote(deckName, modelName, fields))


    def createNote(self, deckName, modelName, fields, tags=[]):
        collection = self.collection()
        if collection is None:
            return

        model = collection.models.byName(modelName)
        if model is None:
            return

        deck = collection.decks.byName(deckName)
        if deck is None:
            return

        note = anki.notes.Note(collection, model)
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


    def startEditing(self):
        self.window().requireReset()


    def stopEditing(self):
        if self.collection() is not None:
            self.window().maybeReset()


    def window(self):
        return aqt.mw


    def addUiAction(self, action):
        self.window().form.menuTools.addAction(action)


    def collection(self):
        return self.window().col


    def modelNames(self):
        collection = self.collection()
        if collection is not None:
            return collection.models.allNames()


    def modelFieldNames(self, modelName):
        collection = self.collection()
        if collection is None:
            return

        model = collection.models.byName(modelName)
        if model is not None:
            return [field['name'] for field in model['flds']]


    def deckNames(self):
        collection = self.collection()
        if collection is not None:
            return collection.decks.allNames()
