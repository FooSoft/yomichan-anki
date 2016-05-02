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
import constants
import reader_util


class AnkiConnect:
    def __init__(self, anki, preferences, interval=50):
        self.preferences = preferences
        self.server      = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.advance)
        self.timer.start(interval)

        self.handlers = {
            'addNote':        self.apiAddNote,
            'apiCanAddNote':  self.apiCanAddNote,
            'apiCanAddNotes': self.apiCanAddNotes,
            'getVersion':     self.apiGetVersion,
        }


    def advance(self):
        enabled = self.preferences['enableRemoteApi']

        if self.server is None and enabled:
            self.server = AjaxServer(self.handler)
            self.server.listen()
        elif self.server is not None and not enabled:
            self.server.close()
            self.server = None

        if self.server is not None:
            self.server.advance()


    def prepareNoteParams(self, definition, mode):
        if definition is None:
            return None

        if mode == 'vocabExp':
            profile = 'vocab'
            markupFunc = reader_util.markupVocabExp
        elif mode == 'vocabReading':
            profile = 'vocab'
            markupFunc = reader_util.markupVocabReading
        elif mode == 'kanji':
            profile = 'kanji'
            markupFunc = reader_util.markupKanji
        else:
            return None

        profile = self.preferences['profiles'].get(profile)
        if profile is None:
            return None

        fields = reader_util.formatFields(
            profile['fields'],
            markupFunc(definition)
        )

        return {
            'deck':   profile['deck'],
            'model':  profile['model'],
            'fields': fields,
            'tags':   self.preferences['tags']
        }


    def handler(self, request):
        action = request.get('action')
        data   = request.get('data')

        self.handlers.get(action, self.apiInvalidRequest)(data)


    def apiAddNote(self, data):
        params = self.prepareNoteParams(data.get('definition'), data.get('mode'))
        if params is not None:
            return self.anki.addNote(params['deck'], params['model'], params['fields'], params['tags'])


    def apiCanAddNote(self, data):
        params = self.prepareNoteParams(data.get('definition'), data.get('mode'))
        if params is not None:
            return self.anki.canAddNote(params['deck'], params['model'], params['fields'])


    def apiCanAddNotes(self, data):
        definitions = data.get('definitions', [])

        for definition in definitions:
            definitions['anki'] = results = {}
            for mode in ['vocabExp', 'vocabReading', 'kanji']:
                params = self.prepareNoteParams(definition, mode)
                results[mode] = params is not None and self.anki.canAddNote(
                    params['deck'],
                    params['model'],
                    params['fields']
                )

        return definitions


    def apiGetVersion(self, data):
        return {'version': constants.c['appVersion']}


    def apiInvalidRequest(self, data):
        return None
