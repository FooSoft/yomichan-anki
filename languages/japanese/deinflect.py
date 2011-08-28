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


import codecs


class Deinflector:
    class __Rule:
        def __init__(self, source, target, types, reason):
            self.source = unicode(source)
            self.target = unicode(target)
            self.types = int(types)
            self.reason = int(reason)


    class __Result:
        def __init__(self, stem, types, conjugations):
            self.stem = unicode(stem)
            self.types = int(types)
            self.conjugations = list(conjugations)


    def __init__(self, filename=None):
        if filename == None:
            self.close()
        else:
            self.load(filename)


    def close(self):
        self.__conjugations = list()
        self.__rules = dict()


    def load(self, filename):
        self.close()

        try:
            with codecs.open(filename, 'rb', 'utf-8') as fp:
                lines = [line.strip() for line in fp.readlines()]
            # ignore the first line which is the file header
            del lines[0]
        except IOError:
            return False

        for line in lines:
            fields = line.split('\t')
            fieldCount = len(fields)

            if fieldCount == 1:
                self.__conjugations.append(fields[0])
            elif fieldCount == 4:
                rule = self.__Rule(*fields)
                sourceLength = len(rule.source)
                if sourceLength not in self.__rules:
                    self.__rules[sourceLength] = list()
                self.__rules[sourceLength].append(rule)
            else:
                self.close()
                return False

        return True


    def deinflect(self, word):
        results = [self.__Result(word, 0xff, list())]
        have = {word: 0}

        for result in results:
            for length, group in sorted(self.__rules.items(), reverse=True):
                if length > len(result.stem):
                    continue

                for rule in group:
                    if result.types & rule.types == 0 or result.stem[-length:] != rule.source:
                        continue

                    new = result.stem[:len(result.stem) - len(rule.source)] + rule.target
                    if len(new) <= 1:
                        continue

                    if new in have:
                        result = results[have[new]]
                        result.types |= (rule.types >> 8)
                        continue

                    have[new] = len(results)

                    conjugations = [self.__conjugations[rule.reason]] + result.conjugations
                    results.append(self.__Result(new, rule.types >> 8, conjugations))

        return [
            (result.stem, u', '.join(result.conjugations), result.types) for result in results
        ]


    def validate(self, types, tags):
        for tag in tags:
            valid = (
                types & 1 and tag == 'v1' or
                types & 2 and tag[:2] == 'v5' or
                types & 4 and tag == 'adj-i' or
                types & 8 and tag == 'vk' or
                types & 16 and tag[:3] == 'vs-'
            )

            if valid:
                return True

        return False
