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
import util


class Translator:
    def __init__(self, deinflector, dictionary):
        self.deinflector = deinflector
        self.dictionary = dictionary


    def findTerm(self, text, wildcards=False):
        text = util.sanitize(text, wildcards=wildcards)

        groups = dict()

        
        length = 0
        for i in xrange(len(text), 0, -1):
            term = text[:i]
            deinflections = self.deinflector.deinflect(term, self.validator)
            groupsBefore = len(groups)
            if deinflections is None:
                self.processTerm(groups, term, wildcards=wildcards)
            else:
                for deinflection in deinflections:
                    self.processTerm(groups, **deinflection)
            if len(groups) > groupsBefore and length == 0:
                length = i

        results = map(self.formatResult, groups.items())
        results = filter(operator.truth, results)
        results = sorted(results, key=lambda d: (len(d['source'])), reverse=True)
        return results, length


    def findCharacters(self, text):
        text = util.sanitize(text, kana=False)
        results = list()

        processed = dict()
        for c in text:
            if c not in processed:
                match = self.dictionary.findCharacter(c)
                if match is not None:
                    results.append(match)
                processed[c] = match

        return results


    def processTerm(self, groups, source, rules=list(), root=str(), wildcards=False):
        root = root or source

        for entry in self.dictionary.findTerm(root, wildcards):
            key = entry['expression'], entry['hanja'], entry['glossary']
            if key not in groups:
                groups[key] = '', source, rules


    def formatResult(self, group):
        (expression, hanja, glossary), (tags, source, rules) = group
        return {
            'expression': expression,
            'hanja': hanja,
            'glossary': glossary,
            'rules': rules,
            'source': source,
            'tags': tags,
            'language': u'Korean'
        }


    def validator(self, term):
        return True
