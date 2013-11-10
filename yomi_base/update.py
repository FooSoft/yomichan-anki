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


from PyQt4 import QtCore
from xml.dom import minidom
import constants
import urllib2


class UpdateFinder(QtCore.QThread):
    updateResult = QtCore.pyqtSignal(str)

    def run(self):
        latest = None
        try:
            fp = urllib2.urlopen(constants.c['urlUpdates'])
            data = fp.read()
            doc = minidom.parseString(data)
            root = doc.documentElement
            if root.nodeName == 'updates':
                latest = root.getAttribute('latest') or None
        except:
            pass
        finally:
            self.updateResult.emit(latest or constants.c['appVersion'])
