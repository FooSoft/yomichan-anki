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


from PyQt4 import QtGui
from yomi_base import japanese
from yomi_base.anki_connect import AnkiConnect
from yomi_base.preference_data import Preferences
from yomi_base.reader import MainWindowReader
import sys


class Yomichan:
    def __init__(self):
        self.language = japanese.initLanguage()

        self.preferences = Preferences()
        self.preferences.load()


class YomichanPlugin(Yomichan):
    def __init__(self):
        Yomichan.__init__(self)

        self.toolIconVisible = False
        self.window          = None
        self.anki            = anki_bridge.Anki()
        self.parent          = self.anki.window()
        self.ankiConnect     = AnkiConnect(self.anki, self.preferences)

        separator = QtGui.QAction(self.parent)
        separator.setSeparator(True)
        self.anki.addUiAction(separator)

        action = QtGui.QAction(QtGui.QIcon(':/img/img/icon_logo_32.png'), '&Yomichan...', self.parent)
        action.setIconVisibleInMenu(True)
        action.setShortcut('Ctrl+Y')
        action.triggered.connect(self.onShowRequest)
        self.anki.addUiAction(action)


    def onShowRequest(self):
        if self.window:
            self.window.setVisible(True)
            self.window.activateWindow()
        else:
            self.window = MainWindowReader(
                self.parent,
                self.preferences,
                self.language,
                None,
                self.anki,
                self.onWindowClose
            )
            self.window.show()


    def onWindowClose(self):
        self.window = None


class YomichanStandalone(Yomichan):
    def __init__(self):
        Yomichan.__init__(self)

        self.application = QtGui.QApplication(sys.argv)
        self.window = MainWindowReader(
            None,
            self.preferences,
            self.language,
            filename=sys.argv[1] if len(sys.argv) >= 2 else None
        )

        self.window.show()
        self.application.exec_()


if __name__ == '__main__':
    instance = YomichanStandalone()
else:
    from yomi_base import anki_bridge
    instance = YomichanPlugin()
