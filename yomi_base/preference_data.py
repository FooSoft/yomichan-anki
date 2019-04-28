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


import codecs
import json
import operator
import os


class Preferences(object):
    def __init__(self):
        self.filename = os.path.expanduser(u'~/.yomichan.json')
        self.defaults = os.path.join(os.path.dirname(__file__), u'defaults.json')
        self.settings = {}


    def __getitem__(self, name):
        return self.settings.get(name)


    def __setitem__(self, name, value):
        self.settings[name] = value


    def load(self):
        with codecs.open(self.defaults, 'rb', 'utf-8') as fp:
            self.settings = json.load(fp)

        try:
            if os.path.exists(self.filename):
                with codecs.open(self.filename, 'rb', 'utf-8') as fp:
                    self.settings.update(json.load(fp))
        except ValueError:
            pass


    def save(self):
        with codecs.open(self.filename, 'wb', 'utf-8') as fp:
            json.dump(self.settings, fp, indent=4, sort_keys=True)


    def filePosition(self, filename):
        matches = filter(lambda f: f['path'] == filename, self['recentFiles'])
        return 0 if len(matches) == 0 else matches[0]['position']


    def recentFiles(self):
        return map(operator.itemgetter('path'), self['recentFiles'])


    def updateFactTags(self, tags):
        if tags in self['tags']:
            self['tags'].remove(tags)
        self['tags'].insert(0, tags)


    def updateRecentFile(self, filename, position):
        self['recentFiles'] = filter(lambda f: f['path'] != filename, self['recentFiles'])
        self['recentFiles'].insert(0, {'path': filename, 'position': position})


    def clearRecentFiles(self):
        self['recentFiles'] = []
