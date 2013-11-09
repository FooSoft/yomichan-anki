# -*- coding: utf-8 -*-

# Copyright (C) 2011  Alex Yatskov
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
import re


class Translator:
    def __init__(self, deinflector, dictionary):
        self.deinflector = deinflector
        self.dictionary = dictionary


    def wordSearch(self, selection):
        groups = dict()

        for i in xrange(len(selection), 0, -1):
            term = selection[:i]

            deinflections = self.deinflector.deinflect(term, self.validator)
            if deinflections is None:
                self.processTerm(groups, term)
            else:
                for deinflection in deinflections:
                    self.processTerm(groups, **deinflection)

        results = map(self.formatResult, groups.items())
        results = filter(operator.truth, results)
        results = sorted(results, key=lambda x: len(x[0]), reverse=True)

        length = 0
        for expression, reading, definition, rules, source in results:
            length = max(length, len(source))
        
        return results, length


    def processTerm(self, groups, source, rules=list(), root=str()):
        root = root or source

        for entry in self.dictionary.findTerm(root):
            expression, reading, definition, tags = entry
            key = expression, reading, definition 
            if key not in groups:
                groups[key] = entry, source, rules


    def formatResult(self, group):
        (expression, reading, definition), (entry, source, rules) = group
        return expression, reading, definition, rules, source


    def validator(self, term):
        results = list()
        for expression, reading, definitions, tags in self.dictionary.findTerm(term):
            results.append(tags)

        return results
