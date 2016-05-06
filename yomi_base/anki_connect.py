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
    def __init__(self, anki, preferences, interval=25):
        self.anki        = anki
        self.preferences = preferences
        self.server      = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.advance)
        self.timer.start(interval)

        self.handlers = {
            'addNote':     self.apiAddNote,
            'canAddNote':  self.apiCanAddNote,
            'canAddNotes': self.apiCanAddNotes,
            'getVersion':  self.apiGetVersion,
        }


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


    def prepareNoteArgs(self, definition, mode):
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

        markup = markupFunc(definition)
        if markup is None:
            return None

        return {
            'deck':   profile['deck'],
            'model':  profile['model'],
            'fields': reader_util.formatFields(profile['fields'], markup),
            'tags':   self.preferences['tags']
        }


    def handler(self, request):
        action = request.get('action')
        params = request.get('params')

        return self.handlers.get(action, self.apiInvalidRequest)(params)


    def apiAddNote(self, params):
        args = self.prepareNoteArgs(params.get('definition'), params.get('mode'))
        if args is not None:
            return self.anki.addNote(args['deck'], args['model'], args['fields'], args['tags'])


    def apiCanAddNote(self, params):
        args = self.prepareNoteArgs(params.get('definition'), params.get('mode'))
        if args is not None:
            return self.anki.canAddNote(args['deck'], args['model'], args['fields'])


    def apiCanAddNotes(self, params):
        results = []
        for definition in params:
            state = {}
            results.append(state)
            for mode in ['vocabExp', 'vocabReading', 'kanji']:
                args = self.prepareNoteArgs(definition, mode)
                state[mode] = args is not None and self.anki.canAddNote(
                    args['deck'],
                    args['model'],
                    args['fields']
                )

        return results


    def apiGetVersion(self, params):
        return {'version': constants.c['appVersion']}


    def apiInvalidRequest(self, params):
        return None
