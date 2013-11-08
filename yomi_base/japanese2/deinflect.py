# -*- coding: utf-8 -*-

#
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
#

import codecs
import json


#
# Deinflection
#

class Deinflection:
    def __init__(self, term, parent=None, tags=list(), rule=str()):
        self.children = list()
        self.term = term
        self.parent = parent
        self.tags = tags
        self.rule = rule


    def deinflect(self, validator, rules):
        for rule, variants in rules.items():
            for variant in variants:
                tagsIn = variant['tagsIn']
                tagsOut = variant['tagsOut']
                kanaIn = variant['kanaIn']
                kanaOut = variant['kanaOut']

                allowed = not self.tags
                for tag in self.tags:
                    if tag in tagsIn:
                        allowed = True

                if not allowed:
                    continue

                for i in xrange(len(kanaIn), len(self.term) + 1):
                    term = self.term[:i]
                    if not term.endswith(kanaIn):
                        continue

                    rebase = term[:-len(kanaIn)] + kanaOut
                    if validator(rebase, self.tags):
                        child = Deinflection(rebase, term, tagsOut, rule)
                        self.children.append(child)
                        child.deinflect(validator, rules)


    def dump(self, depth=0):
        result = u'%s%s' % (u'\t' * depth, self.term)
        if self.rule:
            result += u' (%s %s)' % (self.parent, self.rule)
        result += u'\n'

        for child in self.children:
            result += child.dump(depth + 1)

        return result


    def __str__(self):
        return self.dump()


#
# Deinflector
#

class Deinflector:
    def __init__(self, filename):
        with codecs.open(filename, 'rb', 'utf-8') as fp:
            self.rules = json.load(fp)


    def deinflect(self, term, validator=lambda term, tags: True):
        node = Deinflection(term)
        node.deinflect(validator, self.rules)
        return node
