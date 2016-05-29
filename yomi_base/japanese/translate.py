# -*- coding: utf-8 -*-

# Copyright (C) 2013  Alex Yatskov
# This module is based on Rikaichan code written by Jonathan Zarate
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


class Translator:
    def __init__(self, deinflector, dictionary):
        self.deinflector = deinflector
        self.dictionary  = dictionary


    def findTerm(self, text, wildcards=False):
        if wildcards:
            text = re.sub(u'[\*＊]', u'%', text)
            text = re.sub(u'[\?？]', u'_', text)

        groups = {}
        for i in xrange(len(text), 0, -1):
            term = text[:i]

            dfs = self.deinflector.deinflect(term, lambda term: [d['tags'] for d in self.dictionary.findTerm(term)])
            if dfs is None:
                continue

            for df in dfs:
                self.processTerm(groups, **df)

        definitions = groups.values()
        definitions = sorted(
            definitions,
            reverse=True,
            key=lambda d: (
                len(d['source']),
                'P' in d['tags'],
                -len(d['rules']),
                d['expression']
            )
        )

        length = 0
        for result in definitions:
            length = max(length, len(result['source']))

        return definitions, length


    def findKanji(self, text):
        processed = {}
        results   = []
        for c in text:
            if c not in processed:
                match = self.dictionary.findKanji(c)
                if match is not None:
                    results.append(match)
                processed[c] = match

        return results


    def processTerm(self, groups, source, tags, rules=[], root='', wildcards=False):
        for entry in self.dictionary.findTerm(root, wildcards):
            if entry['id'] in groups:
                continue

            matched = len(tags) == 0
            for tag in tags:
                if tag in entry['tags']:
                    matched = True
                    break

            if matched:
                groups[entry['id']] = {
                    'expression': entry['expression'],
                    'reading':    entry['reading'],
                    'glossary':   entry['glossary'],
                    'tags':       entry['tags'],
                    'source':     source,
                    'rules':      rules
                }
