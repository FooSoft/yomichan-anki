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


import sqlite3


class Dictionary:
    def __init__(self, filename, index=True):
        self.db = sqlite3.connect(filename)
        self.indices = set()


    def findTerm(self, word, wildcards=False):
        self.requireIndex('Terms', 'expression')
        self.requireIndex('Terms', 'reading')

        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM Terms WHERE expression {0} ? OR reading=?'.format('LIKE' if wildcards else '='), (word, word))

        results = []
        for expression, reading, glossary, tags in cursor.fetchall():
            results.append({
                'expression': expression,
                'glossary':   glossary,
                'reading':    reading,
                'tags':       tags.split()
            })

        return results


    def findCharacter(self, character):
        assert len(character) == 1
        self.requireIndex('Kanji', 'character')

        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM Kanji WHERE character=? LIMIT 1', character)

        query = cursor.fetchone()
        if query is not None:
            character, kunyomi, onyomi, glossary = query
            return {
                'character': character,
                'glossary':  glossary,
                'kunyomi':   kunyomi,
                'onyomi':    onyomi
            }


    def requireIndex(self, table, column):
        name = 'index_{0}_{1}'.format(table, column)
        if not self.hasIndex(name):
            self.buildIndex(name, table, column)


    def buildIndex(self, name, table, column):
        cursor = self.db.cursor()
        cursor.execute('CREATE INDEX {0} ON {1}({2})'.format(name, table, column))
        self.db.commit()


    def hasIndex(self, name):
        if name in self.indices:
            return True

        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM sqlite_master WHERE name=?', (name,))
        if len(cursor.fetchall()) == 0:
            return False

        self.indices.update([name])
        return True
