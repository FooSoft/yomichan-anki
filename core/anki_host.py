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


import ankiqt
from anki import hooks, lang
from ankiqt import ui
import re


class Anki:
    def addFact(self, fields, tags=unicode()):
        fact = self.createFact(fields, tags)
        if not fact:
            return None

        action = lang._('Add')

        deck = self.deck()
        deck.setUndoStart(action)
        deck.addFact(fact)
        deck.setUndoEnd(action)
        deck.rebuildCounts()

        ankiqt.mw.updateTitleBar()
        ankiqt.mw.statusView.redraw()

        return fact.id


    def canAddFact(self, fields):
        return bool(self.createFact(fields))


    def createFact(self, fields, tags=unicode()):
        deck = self.deck()
        fact = deck.newFact()
        fact.tags = self.cleanupTags(tags)

        try:
            for field in fact.fields:
                field.value = fields.get(field.getName()) or unicode()
                if not fact.fieldValid(field) or not fact.fieldUnique(field, deck.s):
                    return None
        except KeyError:
            return None

        return fact


    def browseFact(self, factId):
        browser = ui.dialogs.get('CardList', self.window())
        browser.dialog.filterEdit.setText('fid:' + str(factId))
        browser.updateSearch()
        browser.onFact()


    def cleanupTags(self, tags):
        return re.sub('[;,]', unicode(), tags).strip()


    def fields(self):
        return [
            (field.name, field.required, field.unique) for field in self.model().fieldModels
        ]


    def deck(self):
        return self.window().deck


    def model(self):
        return self.deck().currentModel


    def window(self):
        return ankiqt.mw


    def toolsMenu(self):
        return self.window().mainWin.menuTools


    def toolBar(self):
        return self.window().mainWin.toolBar


    def addHook(self, name, callback):
        hooks.addHook(name, callback)


    def removeHook(self, name, callback):
        hooks.removeHook(name, callback)
