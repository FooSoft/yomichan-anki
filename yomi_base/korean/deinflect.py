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

# needed to import javascript
import execjs
import os
os.environ["EXECJS_RUNTIME"] = 'PyV8'
#
# Deinflector
#

class Deinflector:
    def __init__(self,path):
        try:
            self.javascript = execjs.compile(open(path).read())
        except Exception as e:
            self.pyv8 = False
        else:
            self.pyv8 = True
        
    def deinflect(self, term, validator):
        results = list()
        jsQuery = u"stemmer.stem('{0}')".format(term)
        results.append({'source': term, 'rules': list()})
        if self.pyv8:
            try:
                jsResult = self.javascript.eval(jsQuery)
                if jsResult is not None:
                    results.append({'source': jsResult, 'rules':list()})
            except Exception as e:
                print e
        return results