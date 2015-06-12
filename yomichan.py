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
from yomi_base import japanese
from yomi_base.preference_data import Preferences
from yomi_base.reader import MainWindowReader, FileState
import sys
import os
from aqt import mw
from aqt.main import AnkiQt
from aqt.reviewer import Reviewer
from anki.hooks import wrap, addHook
import anki.collection
import anki.sched

class Yomichan:
    def __init__(self):
        self.language = japanese.initLanguage()
        self.preferences = Preferences()
        self.preferences.load()
        self.patched = False

class YomichanPlugin(Yomichan):
    def __init__(self):
        Yomichan.__init__(self)

        self.toolIconVisible = False
        self.window = None
        self.anki = anki_bridge.Anki()
        self.fileCache = dict()

        self.parent = self.anki.window()

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
                self,
                self.parent,
                self.preferences,
                self.language,
                None,
                self.anki,
                self.onWindowClose
            )
            self.window.show()


    def fetchAllCards(self):
        if self.anki is None:
            return None
        profile = self.preferences['profiles'].get('vocab')
        if profile is None:
            return None
            
        allCards = dict()
        
        for cid,value,nid in self.anki.getCards(profile["model"]): 
            allCards[value] = self.anki.collection().getCard(cid)
        return allCards


    def loadAllTexts(self):
        allCards = self.fetchAllCards()
        if allCards is not None:
            mediadir = self.anki.collection().media.dir()
            yomimedia = os.path.join(mediadir,'Yomichan')
            for root,dirs,files in os.walk(yomimedia):
                relDir = os.path.relpath(root,mediadir)
                for file in files:
                    path = os.path.join(relDir,file)
                    fl = FileState(path,self.preferences['stripReadings'])
                    fl.findVocabulary(self.anki.collection().sched,allCards,needContent=False)
                    self.fileCache[u'::'.join(unicode(path).split(os.sep))] = fl
                for dir in dirs:
                    path = os.path.join(relDir,dir)
                    self.fileCache[u'::'.join(unicode(path).split(os.sep))] = None
    


    def onWindowClose(self):
        self.window = None
        
        
    def getFileCache(self):
        return self.fileCache


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
    from yomi_base import anki_bridge
    yomichanInstance = YomichanPlugin()
    def onBeforeStateChange(state, oldState, *args):
        if state == 'overview':
            did = mw.col.decks.selected()
            name = mw.col.decks.nameOrNone(did)
            path = name.split(u'::')
            if path > 0 and path[0] == u'Yomichan':
                yomichanInstance.onShowRequest()
                completePath = mw.col.media.dir()
                for i in path:
                    completePath = os.path.join(completePath,i)
                yomichanInstance.window.openFile(completePath)
                yomichanInstance.window.showMaximized()
        elif state == 'deckBrowser':
            if not yomichanInstance.patched:
                mw.col.sched = anki_bridge.EarlyScheduler(mw.col,yomichanInstance.getFileCache)
                yomichanInstance.patched = True
            yomichanInstance.fileCache = dict()
            yomichanInstance.loadAllTexts()
            
    addHook('beforeStateChange',onBeforeStateChange)