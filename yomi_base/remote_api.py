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


class RemoteApi:
    def __init__(self, anki, enabled, interval=50):
        self.server = None
        self.enable(enabled)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.advance)
        self.timer.start(interval)

        self.handlers = {
            'addNote':       self.apiAddNote,
            'apiCanAddNote': self.apiCanAddNote,
            'getVersion':    self.apiGetVersion,
        }


    def enable(self, enabled=True):
        if self.server is None and enabled:
            self.server = AjaxServer(self.handler)
            self.server.listen()
        elif self.server is not None and not enabled:
            self.server.close()
            self.server = None


    def advance(self):
        if self.server is not None:
            self.server.advance()


    def handler(self, request):
        self.handlers.get(request.get('action'), self.apiInvalidRequest)(request.get('data'))


    def apiAddNote(self, data):
        deckName  = data.get('deckName', unicode())
        modelName = data.get('modelName', unicode())
        fields    = data.get('fields', {})
        tags      = data.get('tags', [])

        return self.anki.addNote(deckName, modelName, fields, tags)


    def apiCanAddNote(self, data):
        deckName  = data.get('deckName', unicode())
        modelName = data.get('modelName', unicode())
        fields    = data.get('fields', {})

        return self.anki.canAddNote(deckName, modelName, fields)


    def apiGetVersion(self, data):
        return {'version': constants.c['appVersion']}


    def apiInvalidRequest(self, data):
        return {}
