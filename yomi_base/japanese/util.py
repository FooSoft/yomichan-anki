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


def isHiragana(c):
    return 0x3040 <= ord(c) < 0x30a0


def isKatakana(c):
    return 0x30a0 <= ord(c) < 0x3100


def isKana(c):
    return isHiragana(c) or isKatakana(c)


def isKanji(c):
    return 0x4e00 <= ord(c) < 0x9fb0 or 0x3400 <= ord(c) < 0x4dc0


def isJapanese(c):
    return isKana(c) or isKanji(c)


def sanitize(text, kana=True, wildcards=False):
    if kana:
        checker = isJapanese
    else:
        checker = isKanji

    if wildcards:
        text = re.sub(u'[\*＊]', u'%', text)
        text = re.sub(u'[\?？]', u'_', text)
        overrides = [u'%', u'_']
    else:
        overrides = list()

    result = u''
    for c in text:
        if checker(c) or c in overrides:
            result += c

    return result
