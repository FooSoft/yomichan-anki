#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (C) 2013  Alex Yatskov
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


from yomi_base import japanese
from yomi_base import korean
from yomi_base.preference_data import Preferences

class Yomichan:
    def __init__(self):
        self.languages = [japanese.initLanguage(),korean.initLanguage()]
        self.preferences = Preferences()
        self.preferences.load()
        
        
    def fetchAllCards(self):
        return None
        
