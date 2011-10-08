# -*- coding: utf-8 -*-
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


import os.path
from dictionary import Dictionary
from deinflect import Deinflector
from translate import Translator


def buildRelPath(path):
    directory = os.path.split(__file__)[0]
    return os.path.join(directory, path)


def initLanguage():
    deinflector = Deinflector(buildRelPath('data/deinflect.dat'))
    dictionary = Dictionary(buildRelPath('data/dict.sqlite'))
    return Translator(deinflector, dictionary)
