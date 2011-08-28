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


import sqlite3
import re


class Dictionary:
    def __init__(self, filename=None):
        if filename == None:
            self.close()
        else:
            self.load(filename)


    def close(self):
        self.__connection = None


    def load(self, filename):
        self.__connection = sqlite3.connect(filename)


    def __find(self, exp, args):
        if self.__connection == None:
            return list()

        entries = list()

        for kanji, kana, entry in self.__connection.cursor().execute(exp, args):
            meanings = entry.split('/')

            if not meanings[-1]:
                items = map(unicode.strip, re.split('[\[\]]', meanings[0]))
                if len(items) > 1:
                    kanji, kana, = items[0], items[1]
                else:
                    kanji, kana = None, items[0]
                del meanings[0], meanings[-1]

            entry = u'; '.join(meanings)
            expression = kanji or kana
            reading = kana if kanji else None

            entries.append((expression, reading, entry))

        return entries


    def findWord(self, word):
        return self.__find(u'select * from dict where kanji=? or kana=? limit 100', (word,) * 2)
