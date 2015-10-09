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


from PyQt4 import QtGui, QtCore
from yomi_base.reader import MainWindowReader
from yomi_base.yomichan import Yomichan
import sys


class YomichanStandalone(Yomichan):
    def __init__(self):
        Yomichan.__init__(self)

        self.application = QtGui.QApplication(sys.argv)
        self.window = MainWindowReader(
            self,
            None,
            self.preferences,
            self.language,
            filename=sys.argv[1] if len(sys.argv) >= 2 else None
        )

        self.window.show()
        self.application.exec_()


if __name__ == '__main__':
    yomichanInstance = YomichanStandalone()
else:
    from yomi_base.anki_bridge import yomichanInstance