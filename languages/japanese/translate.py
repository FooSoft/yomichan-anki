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


import re
from operator import itemgetter


class Translator:
    def __init__(self, deinflector, dictionary):
        self.deinflector = deinflector
        self.dictionary = dictionary


    def wordSearch(self, word, limit, group):
        source, indices = self.convertKatakana(word)

        groups = dict()
        length = 0
        count = 0

        while source:
            for i, (stem, conjugations, types) in enumerate(self.deinflector.deinflect(source)):
                for expression, reading, glossary in self.dictionary.findWord(stem):
                    if count >= limit:
                        break

                    if i > 0:
                        tags = re.split('[,()]', glossary)
                        if not self.deinflector.validate(types, tags):
                            continue

                    length = max(length, indices[len(source) - 1] + 1)

                    key = (expression, glossary, conjugations, source)
                    if key in groups:
                        readings = groups[key][0]
                        if reading and reading not in readings:
                            readings.append(reading)
                            if not group:
                                count += 1
                    else:
                        readings = [reading] if reading else list()
                        groups[key] = (readings, count)
                        count += 1

            source = source[:-1]

        results = list()

        for (expression, glossary, conjugations, source), (readings, count) in groups.items():
            if group:
                readings = u', '.join(readings)
                results.append((expression, readings, glossary, conjugations, source, count))
            elif readings:
                for reading in readings:
                    results.append((expression, reading, glossary, conjugations, source, count))
            else:
                results.append((expression, unicode(), glossary, conjugations, source, count))

        results = [result[:5] for result in sorted(results, key=itemgetter(5))]

        return results, length


    def convertKatakana(self, word):
        kanaHalf = [
            0x3092, 0x3041, 0x3043, 0x3045, 0x3047, 0x3049, 0x3083, 0x3085,
            0x3087, 0x3063, 0x30fc, 0x3042, 0x3044, 0x3046, 0x3048, 0x304a,
            0x304b, 0x304d, 0x304f, 0x3051, 0x3053, 0x3055, 0x3057, 0x3059,
            0x305b, 0x305d, 0x305f, 0x3061, 0x3064, 0x3066, 0x3068, 0x306a,
            0x306b, 0x306c, 0x306d, 0x306e, 0x306f, 0x3072, 0x3075, 0x3078,
            0x307b, 0x307e, 0x307f, 0x3080, 0x3081, 0x3082, 0x3084, 0x3086,
            0x3088, 0x3089, 0x308a, 0x308b, 0x308c, 0x308d, 0x308f, 0x3093
        ]

        kanaVoiced = [
            0x30f4, 0xff74, 0xff75, 0x304c, 0x304e, 0x3050, 0x3052, 0x3054,
            0x3056, 0x3058, 0x305a, 0x305c, 0x305e, 0x3060, 0x3062, 0x3065,
            0x3067, 0x3069, 0xff85, 0xff86, 0xff87, 0xff88, 0xff89, 0x3070,
            0x3073, 0x3076, 0x3079, 0x307c
        ]

        kanaSemiVoiced = [
            0x3071, 0x3074, 0x3077, 0x307a, 0x307d
        ]

        indices = dict()
        result = unicode()
        ordPrev = 0

        for i, char in enumerate(word):
            ordCurr = ord(char)

            if ordCurr <= 0x3000:
                # break upon hitting non-japanese characters
                break
            if 0x30a1 <= ordCurr <= 0x30f3:
                # full-width katakana to hiragana
                ordCurr -= 0x60
            elif 0xff66 <= ordCurr <= 0xff9d:
                # half-width katakana to hiragana
                ordCurr = kanaHalf[ordCurr - 0xff66]
            elif ordCurr == 0xff9e:
                # voiced (used in half-width katakana) to hiragana
                if 0xff73 <= ordPrev <= 0xff8e:
                    result = result[:-1]
                    ordCurr = kanaVoiced[ordPrev - 0xff73]
            elif ordCurr == 0xff9f:
                # semi-voiced (used in half-width katakana) to hiragana
                if 0xff8a <= ordPrev <= 0xff8e:
                    result = result[:-1]
                    ordCurr = kanaSemiVoiced[ordPrev - 0xff8a]
            elif ordCurr == 0xff5e:
                # ignore Japanese ~
                ordPrev = 0
                continue

            indices[len(result)] = i
            result += unichr(ordCurr)
            ordPrev = ord(char)

        return result, indices
