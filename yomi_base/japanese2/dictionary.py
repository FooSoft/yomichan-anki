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


import re
import sqlite3


class Dictionary:
    def __init__(self, filename, index=True):
        self.db = sqlite3.connect(filename)
        self.indices = set()


    def findTerm(self, word):
        cursor = self.db.cursor()

        if not self.hasIndex('TermIndex'):
            cursor.execute('CREATE INDEX TermIndex ON Terms(expression, reading)')
            self.db.commit()

        cursor.execute('SELECT * FROM Terms WHERE expression=? OR reading=?', (word, word))
        return cursor.fetchall()


    def findCharacter(self, character):
        cursor = self.db.cursor()

        if not self.hasIndex('KanjiIndex'):
            cursor.execute('CREATE INDEX KanjiIndex ON Kanji(character)')
            self.db.commit()

        cursor.execute('SELECT * FROM Kanji WHERE character=?', character)
        return cursor.fetchall()


    def hasIndex(self, name):
        if name in self.indices:
            return True

        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM sqlite_master WHERE name=?', (name, ))
        if len(cursor.fetchall()) == 0:
            return False

        self.indices.update([name])
        return True
