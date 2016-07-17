# -*- coding: utf-8 -*-

# Copyright (C) 2016  Alex Yatskov <alex@foosoft.net>
# Author: Alex Yatskov <alex@foosoft.net>
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


from PyQt4 import QtCore
from ajax import AjaxServer
from constants import c


class AnkiConnect:
    def __init__(self, anki, preferences, interval=25):
        self.anki        = anki
        self.preferences = preferences
        self.server      = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.advance)
        self.timer.start(interval)


    def advance(self):
        enabled = self.preferences['enableAnkiConnect']

        if self.server is None and enabled:
            self.server = AjaxServer(self.handler)
            self.server.listen()
        elif self.server is not None and not enabled:
            self.server.close()
            self.server = None

        if self.server is not None:
            self.server.advance()


    def handler(self, request):
        action = 'api_' + (request.get('action') or '')
        if hasattr(self, action):
            return getattr(self, action)(**(request.get('params') or {}))


    def api_deckNames(self):
        return self.anki.deckNames()


    def api_modelNames(self):
        return self.anki.modelNames()


    def api_modelFieldNames(self, modelName):
        return self.anki.modelFieldNames(modelName)


    def api_addNote(self, note):
        return self.anki.addNote(
            note['deckName'],
            note['modelName'],
            note['fields'],
            note['tags'],
            note.get('audio')
        )


    def api_canAddNotes(self, notes):
        results = []
        for note in notes:
            results.append(self.anki.canAddNote(
                note['deckName'],
                note['modelName'],
                note['fields']
            ))

        return results


    def api_features(self):
        features = {}
        for name in dir(self):
            method = getattr(self, name)
            if name.startswith('api_') and callable(method):
                features[name[4:]] = list(method.func_code.co_varnames[1:])

        return features


    def api_version(self):
        return c['apiVersion']
