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

import sys
import os
import time
import random
from PyQt4 import QtGui, QtCore
import anki
import aqt
from anki.hooks import addHook
import anki.collection
from yomichan import Yomichan
from yomi_base.reader import MainWindowReader
from yomi_base.file_state import FileState
from yomi_base.scheduler import Scheduler
from anki.models import defaultModel,defaultField,defaultTemplate
from anki.utils import ids2str, intTime


class Anki:
    def createYomichanModel(self):
        models = self.collection().models
        if u'YomichanSentence' not in models.allNames():
            model = models.new(u'YomichanSentence')
            model['css'] = """\
.card {
 font-family: arial;
 font-size: 22px;
 text-align: center;
 color: black;
 background-color: white;
}

.card1 { background-color: #ffff7f; }
.card2 { background-color: #efff7f; }
            """
            for field in [u'Expression',u'Translation',u'Reading']:
                models.addField(model,models.newField(field))
            template = models.newTemplate(u'Production')
            template['qfmt'] = u'{{Translation}}'
            template['afmt'] = u'{{FrontSide}}<hr>{{Expression}}'
            models.addTemplate(model,template)
            models.add(model)
            models.flush()
        if u'YomichanKanji' not in models.allNames():
            model = models.new(u'YomichanKanji')
            model['css'] = """\
.card {
 font-family: arial;
 font-size: 22px;
 text-align: center;
 color: black;
 background-color: white;
}

.card1 { background-color: #ffff7f; }
.card2 { background-color: #efff7f; }
            """
            for field in [u'Kanji',u'Onyomi',u'Kunyomi',u'Glossary']:
                models.addField(model,models.newField(field))
            template = models.newTemplate(u'Recognition')
            template['qfmt'] = u'{{Kanji}}'
            template['afmt'] = u'{{FrontSide}}<hr>{{Glossary}}'
            models.addTemplate(model,template)
            models.add(model)
            models.flush()
        if u'Yomichan' not in models.allNames():
            model = models.new(u'Yomichan')
            model['css'] = """\
.card {
 font-family: arial;
 font-size: 22px;
 text-align: center;
 color: black;
 background-color: white;
}

.card1 { background-color: #ffff7f; }
.card2 { background-color: #efff7f; }
            """
            for field in [u'Vocabulary-Furigana',u'v',u'Vocabulary-English',u'Expression',u'Reading',u'Sentence-English',u'Video',u'Examples+']:
                models.addField(model,models.newField(field))
            template = models.newTemplate(u'Recognition')
            template['qfmt'] = u'<span style="font-size: 60px">{{v}}</span><br><br><br>\n<span style="font-size: 20px; font-family: \uff2d\uff33 \u30b4\u30b7\u30c3\u30af;">{{kanji:Reading}}</span>\n{{^Reading}}\n<span style="font-size: 20px;">{{kanji:Expression}}</span>\n{{/Reading}}'
            template['afmt'] = u'<span style="font-size: 50px; font-family: \uff2d\uff33 \u30b4\u30b7\u30c3\u30af;">{{furigana:Vocabulary-Furigana}}</span><br>\n{{^Vocabulary-Furigana}}\n<span style="font-size: 30px"></span><br>\n<span style="font-size: 60px">{{v}}</span><br><br>\n{{/Vocabulary-Furigana}}\n<span style="font-size: 20px; font-family: \uff2d\uff33 \u30b4\u30b7\u30c3\u30af;">{{furigana:Reading}}</span><br>\n{{^Reading}}\n<span style="font-size: 20px;">{{furigana:Expression}}</span>\n{{/Reading}}\n<hr id=answer>\n<img src="{{Video}}"/><br>\n<span style="font-size: 12px; ">{{Vocabulary-English}}</span> <span style="font-size: 15px; color: #5555ff"></span><br>\n<br>\n<span style="font-size: 15px; ">{{Sentence-English}}</span>\n'
            models.addTemplate(model,template)
            models.add(model)
            models.flush()
        decks = self.collection().decks
        if u'Yomichan' not in decks.allNames():
            decks.id(u'Yomichan')
            decks.id(u'YomichanCards')
            
            
    def addNote(self, deckName, modelName, fields, tags=list()):
        note = self.createNote(deckName, modelName, fields, tags)
        if note is not None:
            collection = self.collection()
            collection.addNote(note)
            collection.autosave()
            self.startEditing()
            return note.id


    def canAddNote(self, deckName, modelName, fields):
        return bool(self.createNote(deckName, modelName, fields))


    def createNote(self, deckName, modelName, fields, tags=list()):
        model = self.models().byName(modelName)
        if model is None:
            return None

        deck = self.decks().byName(deckName)
        if deck is None:
            return None

        note = anki.notes.Note(self.collection(), model)
        note.model()['did'] = deck['id']
        note.tags = tags

        for name, value in fields.items():
            if name in note:
                note[name] = value

        if not note.dupeOrEmpty():
            return note


    def browse(self, query):
        browser = aqt.dialogs.open('Browser', self.window())
        browser.form.searchEdit.lineEdit().setText(u' '.join([u'{0}:{1}'.format(key,value) for key,value in query.items()]))
        browser.onSearch()
        
    
    def getNotes(self, modelName, key, value):
        return self.collection().findNotes(key + u':' + value + u' note:' + modelName)
        
        
    def getCards(self, modelName, onlyFirst = False):
        model = self.models().byName(modelName)
        modelid = int(model[u"id"])
        query = "select " + ("min(c.id)" if onlyFirst else "c.id")
        query+= ",n.sfld,n.id from cards c "
        query+= "join notes n on (c.nid = n.id) " 
        query+= "where n.mid=%d" % (modelid)
        if onlyFirst: query+= "group by n.id"
        return self.collection().db.execute(query)
        
    
    def getCardsByNote(self, modelName, key, value):
        return self.collection().findCards(key + u':"' + value + u'" note:' + modelName)

    def getCardsByNoteAndNotInDeck(self, modelName, values, did):
        model = self.models().byName(modelName)
        modelid = int(model[u"id"])
        query = u"select c.id from cards c "
        query+= u"join notes n on (c.nid = n.id) " 
        query+= u"where n.mid=%d " % (modelid)
        query+= u"and c.did!=%d " % (did)
        query+= u"and n.sfld in " + (u"(%s)" % u",".join([u"'%s'"%(s) for s in values]))
        self.query = query
        return self.collection().db.execute(query)
        
    
    def getModelKey(self, modelName):
        model = self.collection().models.byName(modelName)
        if model is None:
            return None
        frstfld = model[u"flds"][0]
        return frstfld[u"name"]
        

    def startEditing(self):
        self.window().requireReset()


    def stopEditing(self):
        if self.collection():
            self.window().maybeReset()


    def window(self):
        return aqt.mw


    def addUiAction(self, action):
        self.window().form.menuTools.addAction(action)


    def collection(self):
        return self.window().col


    def models(self):
        return self.collection().models


    def modelNames(self):
        return self.models().allNames()


    def modelFieldNames(self, modelName):
        model = self.models().byName(modelName)
        if model is not None:
            return [field['name'] for field in model['flds']]


    def decks(self):
        return self.collection().decks


    def deckNames(self):
        return self.decks().allNames()
    
    def moveCards(self,cardKeys,model,deck):
        key = self.getModelKey(model)                                                  
        did = self.collection().decks.id(deck)
        cids = [int(cid[0]) for cid in self.getCardsByNoteAndNotInDeck(profile['model'],cardKeys,did)]
        updateCards(cids,did)
        
    def updateCards(self,cids,did):
        deck = self.collection().decks.get(did)
        self.window().checkpoint(_("Update cards"))
        if not deck['dyn']:
            mod = intTime()
            usn = self.collection().usn()
            scids = ids2str(cids)
            self.collection().sched.remFromDyn(cids)
            self.collection().db.execute("""update cards set usn=?, mod=?, did=? where id in """ + scids, usn, mod, did)
        self.window().requireReset()


class YomichanPlugin(Yomichan):
    def __init__(self):
        Yomichan.__init__(self)

        self.toolIconVisible = False
        self.window = None
        self.anki = Anki()
        self.fileCache = dict()

        self.parent = None #self.anki.window()

        separator = QtGui.QAction(self.anki.window())
        separator.setSeparator(True)
        self.anki.addUiAction(separator)

        action = QtGui.QAction(QtGui.QIcon(':/img/img/icon_logo_32.png'), '&Yomichan...', self.anki.window())
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
                self.languages,
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


    def loadAllTexts(self,rootDir=None):
        if rootDir is None:
            rootDir = u"Yomichan"
        
        oldCache = self.fileCache
        self.fileCache = dict()
        allCards = self.fetchAllCards()
        if allCards is not None:
            mediadir = self.anki.collection().media.dir()
            yomimedia = os.path.join(mediadir,rootDir)
            def processFile(file,relDir):
                if file[-4:] == '.txt':
                    path = os.path.join(relDir,file)
                    fullPath = u'::'.join(unicode(path).split(os.sep))
                    if fullPath in oldCache:
                        fileState = oldCache[fullPath]
                        fileState.load()
                    else:
                        fileState = FileState(path,self.preferences['stripReadings'])
                    self.fileCache[fullPath] = fileState
                    fileState.findVocabulary(self.anki.collection().sched,allCards,needContent=False)
            if os.path.isdir(yomimedia):
                for root,dirs,files in os.walk(yomimedia):
                    relDir = os.path.relpath(root,mediadir)
                    for file in files:
                        processFile(file,relDir)
                    for dir in dirs:
                        path = os.path.join(relDir,dir)
                        self.fileCache[u'::'.join(unicode(path).split(os.sep))] = None
            elif os.path.isfile(yomimedia):
                processFile(os.path.basename(yomimedia),os.path.dirname(yomimedia))
            


    def onWindowClose(self):
        self.window = None
        
        
    def getFileCache(self):
        return self.fileCache


yomichanInstance = YomichanPlugin()        
        
def onBeforeStateChange(state, oldState, *args):
    yomichanInstance.newestState = state
    yomichanInstance.anki.createYomichanModel()
    if state == 'overview':
        did = aqt.mw.col.decks.selected()
        name = aqt.mw.col.decks.nameOrNone(did)
        path = name.split(u'::')
        if len(path) > 0 and path[0] == u'Yomichan':
            yomichanInstance.onShowRequest()
            completePath = aqt.mw.col.media.dir()
            for i in path:
                completePath = os.path.join(completePath,i)
            if os.path.isdir(completePath):
                maxDue = 0
                maxDueDeck = None
                for name, id in aqt.mw.col.decks.children(did):
                    if aqt.mw.col.sched.dueCache[name] >= maxDue:
                        maxDue = aqt.mw.col.sched.dueCache[name]
                        maxDueDeck = name
                if maxDueDeck is None:
                    return
                path = maxDueDeck.split(u'::')
                completePath = aqt.mw.col.media.dir()
                for i in path:
                    completePath = os.path.join(completePath,i)
                if os.path.isdir(completePath):
                    return
            if yomichanInstance.window.state.filename != completePath:
                yomichanInstance.window.openFile(completePath)
                dirName = os.path.dirname(os.path.realpath(completePath))
                fileName = os.path.basename(os.path.splitext(completePath)[0])
                try:
                    for file in os.listdir(dirName):
                        if not file.endswith(".txt") and fileName == os.path.basename(os.path.splitext(file)[0]):
                            openFile = os.path.join(dirName,file)
                            if sys.platform == 'linux2':
                                subprocess.call(["xdg*-open", openFile])
                            else:
                                os.startfile(openFile)
                except:
                    fileName = fileName #do nothing
                yomichanInstance.window.showMaximized()
    elif state == 'deckBrowser':
        if not getattr(aqt.mw.col.sched,"earlyAnswerCard",None):
            aqt.mw.col.sched = Scheduler(aqt.mw.col,yomichanInstance.getFileCache,scheduleVariationPercent = yomichanInstance.preferences['scheduleVariationPercent'],weekDays = yomichanInstance.preferences['weekDays'])
        yomichanInstance.loadAllTexts()
        yomichanDeck = aqt.mw.col.decks.byName(u'Yomichan')
        for name,id in aqt.mw.col.decks.children(yomichanDeck['id']):
            if name not in yomichanInstance.fileCache and aqt.mw.col.decks.get(id)['id']!=1:
                aqt.mw.col.decks.rem(id)
addHook('beforeStateChange',onBeforeStateChange)
    


def onSearch(cmds):
    def findByYomichanFile(oldfn):
        def inner((val,args)):
            if(val.startswith(u"Yomichan")):
                yomichanInstance.searchPath = val.replace(u"::",os.sep)
                yomichanInstance.loadAllTexts(val.replace(u"::",os.sep))
                words = set()
                for text,state in yomichanInstance.fileCache.items():
                    if state is not None:
                        words |= set(state.wordsAll.keys())
                arg = "(" + ",".join(["\""+val+"\"" for val in words]) + ")"
                where = "(n.sfld in " + arg + ")"
                yomichanInstance.where = where
                return where
            else:
                return oldfn((val,args))
        return inner    
    cmds['deck'] = findByYomichanFile(cmds['deck'])    
addHook('search',onSearch)