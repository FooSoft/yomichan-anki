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


def isHangul(c):
    return 0xac00 <= ord(c) <= 0xd7a3

def isJamo(c):
    return 0x1100 <= ord(c) <= 0x11ff or 0x3130 <= ord(c) <= 0x318f or 0xa960 <= ord(c) <= 0xa97f or 0xd7b0 <= ord(c) <= 0xd7ff

def isHanja(c):
    return 0x4e00 <= ord(c) < 0x9fb0 or 0x3400 <= ord(c) < 0x4dc0


def isKorean(c):
    return isHangul(c) or isHanja(c)


def sanitize(text, noHanja=True, wildcards=False):
    if noHanja:
        checker = isKorean
    else:
        checker = isHanja        

    if wildcards:
        text = re.sub(u'[\*＊]', u'%', text)
        text = re.sub(u'[\?？]', u'_', text)
        overrides = [u'%', u'_']
    else:
        overrides = list()

    result = unicode()
    for c in text:
        if checker(c) or c in overrides:
            result += c

    return result
