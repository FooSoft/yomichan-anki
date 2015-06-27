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
from PyQt4.QtWebKit import QWebView
from time import time
#
# Deinflector
#

class Deinflector:
    def __init__(self,path):
        self.iterations = 0
        self.totalTime = 0
        #app = QApplication(sys.argv) - not needed because we have a QApp already
        self.view = QWebView()
        with open(path) as fp:
            js = fp.read()
        self.view.page().mainFrame().evaluateJavaScript(js)    
        
    def deinflect(self, term, validator):
        start = time()
        results = list()
        jsQuery = u"stemmer.getStem('{0}')".format(term)
        jsResult = self.view.page().mainFrame().evaluateJavaScript(jsQuery)
        print jsResult
        results.append({'source': term, 'rules': list()})
        if jsResult is not None:
            results.append({'source': u''.join(map(unichr,map(int,jsResult))), 'rules':list()})
        self.iterations += 1
        self.totalTime += (time()-start)
        return results