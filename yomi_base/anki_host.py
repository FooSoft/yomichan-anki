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
#from anki import hooks, lang
#from ankiqt import ui
import re


class Anki:
    def addNote(self, fields, tags=unicode()):
        note = self.createNote(fields, tags)
        if not note:
            return None

        action = lang._('Add')

        collection = self.collection()
        collection.setUndoStart(action)
        collection.addNote(note, False)
        collection.setUndoEnd(action)
        collection.rebuildCounts()

        ankiqt.mw.updateTitleBar()
        ankiqt.mw.statusView.redraw()

        return note.id


    def canAddNote(self, fields):
        return bool(self.createNote(fields))


    def createNote(self, fields, tags=unicode()):
        collection = self.collection()
        note = collection.newnote()
        note.tags = self.cleanupTags(tags)

        try:
            for field in note.fields:
                field.value = fields.get(field.getName()) or unicode()
                if not note.fieldValid(field) or not note.fieldUnique(field, collection.s):
                    return None
        except KeyError:
            return None

        return note


    def browseNote(self, noteId):
        browser = ui.dialogs.get('CardList', self.window())
        browser.dialog.filterEdit.setText('fid:' + str(noteId))
        browser.updateSearch()
        browser.onnote()


    def cleanupTags(self, tags):
        return re.sub('[;,]', unicode(), tags).strip()


    def fields(self):
        return [field['name'] for field in self.currentModel()['flds']]


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


    def currentModel(self):
        return self.models().current()
