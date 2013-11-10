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


import operator


class Translator:
    def __init__(self, deinflector, dictionary):
        self.deinflector = deinflector
        self.dictionary = dictionary


    def findTerm(self, selection, partial=False):
        groups = dict()

        for i in xrange(len(selection), 0, -1):
            term = selection[:i]

            deinflections = self.deinflector.deinflect(term, self.validator)
            if deinflections is None:
                self.processTerm(groups, term, partial=partial)
            else:
                for deinflection in deinflections:
                    self.processTerm(groups, **deinflection)

        results = map(self.formatResult, groups.items())
        results = filter(operator.truth, results)
        results = sorted(results, key=lambda x: len(x['source']), reverse=True)

        length = 0
        for result in results:
            length = max(length, len(result['source']))
        
        return results, length


    def processTerm(self, groups, source, rules=list(), root=str(), partial=False):
        root = root or source

        for entry in self.dictionary.findTerm(root, partial):
            key = entry['expression'], entry['reading'], entry['glossary']
            if key not in groups:
                groups[key] = entry, source, rules


    def formatResult(self, group):
        (expression, reading, glossary), (entry, source, rules) = group
        return {
            'expression': expression,
            'reading': reading,
            'glossary': glossary,
            'rules': rules,
            'source': source
        }


    def validator(self, term):
        return [d['tags'] for d in self.dictionary.findTerm(term)]
