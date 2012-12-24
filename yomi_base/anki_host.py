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
    def addNote(self, fields, tags=unicode()):
        note = self.createNote(fields, tags)
        if not note:
            return None

        self.collection().addNote(note)
        self.window().requireReset()

        return note.id


    def canAddNote(self, fields):
        return bool(self.createNote(fields))


    def createNote(self, fields, tags=unicode()):
        note = self.collection().newNote()

        note.tags = re.split('[;,\s]', tags)
        for name, value in fields.items():
            note[name] = value

        return None if note.dumpOrEmpty() else note


    def browseNote(self, noteId):
        browser = ui.dialogs.get('CardList', self.window())
        browser.dialog.filterEdit.setText('fid:' + str(noteId))
        browser.updateSearch()
        browser.onnote()


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
        for model in self.models().models.values():
            if model['name'] == name:
                return model


    def decks(self):
        return self.collection().decks


    def deckNames(self):
        return self.decks().allNames()


    def findDeck(self, name):
        for deck in self.decks().decks.values():
            if deck['name'] == name:
                return deck

