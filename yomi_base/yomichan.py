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
import urllib2



class Yomichan:
    def __init__(self):
        self.languages = dict()
        self.preferences = Preferences()
        self.preferences.load()
        
        if self.preferences.settings['japanese']:
            self.languages['japanese'] = japanese.initLanguage()
        if self.preferences.settings['korean']:
            self.languages['korean'] = korean.initLanguage()
            
        for sub in self.preferences['subscriptions']:
            try:
                fp = urllib2.urlopen(sub['source'])
                f = open(sub['target'], 'w')
                f.write(fp.read())
                f.close()
                fp.close()
            except:
                donothing = True
        
    def fetchAllCards(self):
        return None
        
