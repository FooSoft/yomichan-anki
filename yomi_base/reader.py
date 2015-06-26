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
import about
import constants
import gen.reader_ui
import japanese.util
import os
import preferences
import reader_util
import updates
import sys
import time

class FileState:
    def __init__(self,fn,stripReadings=False):
        self.wordsAll = dict()
        self.wordsBad = dict()
        self.wordsMarkup = dict()
        self.sep = u"\U00012000"
        self.lineBreak = u"\U00012001"
        self.wordsNotFound = []
        self.dueness = 0.0
        self.wrong = 0
        self.correct = 0
        self.resetTimer()
        self.stripReadings = stripReadings
        if fn is None:
            self.filename = u''
        else:
            self.filename = unicode(fn)
            self.load()
    
    def load(self):
        with open(self.filename) as fp:
            self.content = fp.read()

        self.content, self.encoding = reader_util.decodeContent(self.content)
        if self.stripReadings:
            self.content = reader_util.stripReadings(self.content)
    

    def resetTimer(self):
        self.timerStarted = time.time()
    
            
    def getPlainVocabularyList(self):
        return  u'### VOCABULARY IN THIS TEXT ###\n'+u'\n'.join(self.wordsAll.keys())+u'\n'.join(self.wordsNotFound) 

    def getExportVocabularyList(self,allowedTags):
        def access(x,y):
            if y not in x:
                return u''
            else:
                return x[y]
        #don't export filename, because it's unnecessary for importing
        if 'filename' in allowedTags:
            allowedTags.remove('filename')
        vocabularyDefinitions = [self.sep.join([x]+([access(self.wordsMarkup[x],y).replace(u'\n',self.lineBreak) for y in allowedTags])) for x in self.wordsAll.keys()]
        return  u'### VOCABULARY IN THIS TEXT (EXPORT)###\n'+ self.sep.join(allowedTags) +u'\n'+ u'\n'.join(vocabularyDefinitions)+u'\n'.join(self.wordsNotFound) 
	
    
    def overwriteVocabulary(self,value,card):
        self.wordsAll[value] = card
        if value in self.wordsBad:
            self.wordsBad[value] = card
    
    
    def addVocabulary(self,value,card,addToBadListToo = True):
        self.wordsAll[value] = card
        if addToBadListToo:
            self.wordsBad[value] = card             
    
    def addMarkup(self,value,markup):
        self.wordsMarkup[value] = markup
        
    def findVocabulary(self,sched,allCards,needContent=True):
        lines = self.content.splitlines()
        foundSeparation = False
        self.exportedVocab = False
        exportedTags = None
        self.content = u''
        self.dueness = 0.0
        self.foundvocabs = 0
        self.wordsNotFound = []
        for line in lines:
            if self.exportedVocab and not exportedTags:
                exportedTags = line.split(self.sep)
            elif foundSeparation:
                if self.exportedVocab:
                    definitions = line.split(self.sep)
                    line = definitions.pop(0)
                    markup = dict()
                    for i, field in enumerate(definitions):
                        if i>= len(exportedTags):
                            break
                        markup[exportedTags[i]] = field.replace(self.lineBreak,u'\n')
                    markup['filename'] = self.filename
                    self.wordsMarkup[line] = markup
                if line in allCards:
                    card = allCards[line]
                    self.dueness += sched._smoothedIvl(card)
                    self.wordsAll[line] = card
                    self.foundvocabs += 1
                else:
                    self.wordsNotFound.append(line)
            elif line == u'### VOCABULARY IN THIS TEXT ###':
                foundSeparation = True
            elif line == u'### VOCABULARY IN THIS TEXT (EXPORT)###':
                foundSeparation = True
                self.exportedVocab = True
            elif needContent:
                self.content += line + u'\n'
        
        
    def onLearnVocabularyList(self,sched):
        self.correct = 0
        self.wrong = 0
        self.timeTotal = time.time() - self.timerStarted
        self.timePerWord = self.timeTotal / len(self.wordsAll)
        for word in self.wordsAll:
            if word in self.wordsBad:
                sched.earlyAnswerCard(self.wordsBad[word],1,self.timePerWord)
                self.wrong += 1
            else:
                sched.earlyAnswerCard(self.wordsAll[word],3,self.timePerWord)
                self.correct += 1



class MainWindowReader(QtGui.QMainWindow, gen.reader_ui.Ui_MainWindowReader):
            
                
    class State:
        def __init__(self):
            self.filename = unicode()
            self.kanjiDefs = list()
            self.scanPosition = 0
            self.searchPosition = 0
            self.searchText = unicode()
            self.vocabDefs = list()


    def __init__(self, plugin, parent, preferences, language, filename=None, anki=None, closed=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.textContent.mouseMoveEvent = self.onContentMouseMove
        self.textContent.mousePressEvent = self.onContentMousePress
        self.dockAnki.setEnabled(anki is not None)
        self.currentFile = None
        self.plugin = plugin
        self.preferences = preferences
        self.anki = anki
        self.facts = list()
        self.overwritable = [False] * 10
        self.overwritableReading = [False] * 10
        self.freshlyAdded = []
        self.listDefinitions.clear()
        self.closed = closed
        self.language = language
        self.state = self.State()
        self.updates = updates.UpdateFinder()
        self.zoom = 0
        self.applyPreferences()
        self.updateRecentFiles()
        self.updateVocabDefs()
        self.updateKanjiDefs()

        if filename is not None:
            self.openFile(filename)
        elif self.preferences['rememberTextContent']:
            self.textContent.setPlainText(self.preferences['textContent'])
        elif self.preferences['loadRecentFile']:
            filenames = self.preferences.recentFiles()
            if len(filenames) > 0 and os.path.isfile(filenames[0]):
                self.openFile(filenames[0])
        elif self.anki is not None:
            self.currentFile = FileState(filename, self.anki.collection().sched)

        self.actionAbout.triggered.connect(self.onActionAbout)
        self.actionFeedback.triggered.connect(self.onActionFeedback)
        self.actionFind.triggered.connect(self.onActionFind)
        self.actionFindNext.triggered.connect(self.onActionFindNext)
        self.actionHomepage.triggered.connect(self.onActionHomepage)
        self.actionKindleDeck.triggered.connect(self.onActionKindleDeck)
        self.actionWordList.triggered.connect(self.onActionWordList)
        self.actionOpen.triggered.connect(self.onActionOpen)
        self.actionSave.triggered.connect(self.onActionSave)
        self.actionPreferences.triggered.connect(self.onActionPreferences)
        self.actionToggleWrap.toggled.connect(self.onActionToggleWrap)
        self.actionZoomIn.triggered.connect(self.onActionZoomIn)
        self.actionZoomOut.triggered.connect(self.onActionZoomOut)
        self.actionZoomReset.triggered.connect(self.onActionZoomReset)
        self.dockAnki.visibilityChanged.connect(self.onVisibilityChanged)
        self.dockKanji.visibilityChanged.connect(self.onVisibilityChanged)
        self.dockVocab.visibilityChanged.connect(self.onVisibilityChanged)
        if self.anki is not None:
            self.learnVocabulary.clicked.connect(self.onLearnVocabularyList)
        self.listDefinitions.itemDoubleClicked.connect(self.onDefinitionDoubleClicked)
        self.textKanjiDefs.anchorClicked.connect(self.onKanjiDefsAnchorClicked)
        self.textKanjiSearch.returnPressed.connect(self.onKanjiDefSearchReturn)
        self.textVocabDefs.anchorClicked.connect(self.onVocabDefsAnchorClicked)
        self.textVocabSearch.returnPressed.connect(self.onVocabDefSearchReturn)
        self.updates.updateResult.connect(self.onUpdaterSearchResult)

        if self.preferences['checkForUpdates']:
            self.updates.start()

    
    def onLearnVocabularyList(self):
        if self.anki is None:
            return
        self.currentFile.onLearnVocabularyList(self.anki.collection().sched)
        totalSeconds = int(self.currentFile.timeTotal) %  60
        totalMinutes = int(self.currentFile.timeTotal) // 60
        perCardSeconds = int(self.currentFile.timePerWord) %  60
        perCardMinutes = int(self.currentFile.timePerWord) // 60
        QtGui.QMessageBox.information(
            self,
            'Yomichan', '{0} correct and {1} wrong\n{2} minutes {3} seconds for all\n{4} minutes {5} seconds per card'
            .format(self.currentFile.correct,self.currentFile.wrong,
                totalMinutes,totalSeconds,
                perCardMinutes,perCardSeconds)
        )


    def applyPreferences(self):
        if self.preferences['windowState'] is not None:
            self.restoreState(QtCore.QByteArray.fromBase64(self.preferences['windowState']))
        if self.preferences['windowPosition'] is not None:
            self.move(QtCore.QPoint(*self.preferences['windowPosition']))
        if self.preferences['windowSize'] is not None:
            self.resize(QtCore.QSize(*self.preferences['windowSize']))

        self.comboTags.addItems(self.preferences['tags'])
        self.applyPreferencesContent()

        if self.preferences['firstRun']:
            QtGui.QMessageBox.information(
                self,
                'Yomichan',
                'This may be the first time you are running Yomichan.\nPlease take some time to configure this extension.'
            )

            self.onActionPreferences()

    def applyPreferencesContent(self):
        palette = self.textContent.palette()
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(self.preferences['bgColor']))
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor(self.preferences['fgColor']))
        self.textContent.setPalette(palette)

        self.textContent.setReadOnly(not self.preferences['allowEditing'])
        self.textContent.setAttribute(QtCore.Qt.WA_InputMethodEnabled)

        font = self.textContent.font()
        font.setFamily(self.preferences['fontFamily'])
        font.setPointSize(self.preferences['fontSize'] + self.zoom)
        self.textContent.setLineWrapMode(QtGui.QPlainTextEdit.WidgetWidth if self.preferences['wordWrap'] else QtGui.QPlainTextEdit.NoWrap)
        self.textContent.setFont(font)

        self.actionToggleWrap.setChecked(self.preferences['wordWrap'])


    def closeEvent(self, event):
        self.closeFile()
        self.preferences['windowState'] = str(self.saveState().toBase64())
        self.preferences.save()

        if self.anki is not None:
            self.anki.stopEditing()

        if self.closed is not None:
            self.closed()


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self.updateSampleFromPosition()
        elif (ord('0') <= event.key() <= ord('9') or (QtCore.Qt.Key_F1 <= event.key() <= QtCore.Qt.Key_F10)) and self.anki is not None:
            if ord('0') <= event.key() <= ord('9'):
                index = (event.key() - ord('0') - 1) % 10
            else:
                index = (event.key() - QtCore.Qt.Key_F1) % 10
            if event.modifiers() & QtCore.Qt.ShiftModifier:
                if event.modifiers() & QtCore.Qt.ControlModifier:
                    self.executeKanjiCommand('addKanji', index)
            else:
                if event.modifiers() & QtCore.Qt.ControlModifier:
                    if self.overwritable[index]:
                        self.executeVocabCommand('overwriteVocabExp', index)
                    else:
                        self.executeVocabCommand('addVocabExp', index)
                if event.modifiers() & QtCore.Qt.AltModifier:
                    if self.overwritableReading[index]:
                        self.executeVocabCommand('overwriteVocabReading', index)
                    else:
                        self.executeVocabCommand('addVocabReading', index)
        elif event.key() == ord('[') and self.state.scanPosition > 0:
            self.state.scanPosition -= 1
            self.updateSampleFromPosition()
        elif event.key() == ord(']') and self.state.scanPosition < len(self.textContent.toPlainText()) - 1:
            self.state.scanPosition += 1
            self.updateSampleFromPosition()
            


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()


    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        self.openFile(url.toLocalFile())

        
    def moveEvent(self, event):
        self.preferences['windowPosition'] = event.pos().x(), event.pos().y()


    def resizeEvent(self, event):
        self.preferences['windowSize'] = event.size().width(), event.size().height()


    def onActionOpen(self):
        filename = QtGui.QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a file to open',
            directory=self.state.filename,
            filter='Text files (*.txt);;All files (*.*)'
        )
        if filename:
            self.openFile(filename)
    
    def onActionSave(self):
        filename = QtGui.QFileDialog.getSaveFileName(
            parent=self,
            caption='Select a file to save',
            directory=self.state.filename,
            filter='Text files (*.txt);;All files (*.*)'
        )
        if filename:
            self.saveFile(filename)
    

    def onActionKindleDeck(self):
        filename = QtGui.QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a Kindle deck to import',
            filter='Deck files (*.db)'
        )
        if filename:
            words = reader_util.extractKindleDeck(filename)
            self.importWordList(words)


    def onActionWordList(self):
        filename = QtGui.QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a word list file to import',
            filter='Text files (*.txt);;All files (*.*)'
        )
        if filename:
            words = reader_util.extractWordList(filename)
            self.importWordList(words)
                                            
          
    def onActionPreferences(self):
        dialog = preferences.DialogPreferences(self, self.preferences, self.anki)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.applyPreferencesContent()


    def onActionAbout(self):
        dialog = about.DialogAbout(self)
        dialog.exec_()


    def onActionZoomIn(self):
        font = self.textContent.font()
        if font.pointSize() < 72:
            font.setPointSize(font.pointSize() + 1)
            self.textContent.setFont(font)
            self.zoom += 1


    def onActionZoomOut(self):
        font = self.textContent.font()
        if font.pointSize() > 1:
            font.setPointSize(font.pointSize() - 1)
            self.textContent.setFont(font)
            self.zoom -= 1


    def onActionZoomReset(self):
        if self.zoom:
            font = self.textContent.font()
            font.setPointSize(font.pointSize() - self.zoom)
            self.textContent.setFont(font)
            self.zoom = 0


    def onActionFind(self):
        searchText = self.state.searchText

        cursor = self.textContent.textCursor()
        if cursor.hasSelection():
            searchText = cursor.selectedText()

        searchText, ok = QtGui.QInputDialog.getText(self, 'Find', 'Search text:', text=searchText)
        if searchText and ok:
            self.findText(searchText)


    def onActionFindNext(self):
        if self.state.searchText:
            self.findText(self.state.searchText)


    def onActionToggleWrap(self, wrap):
        self.preferences['wordWrap'] = wrap
        self.textContent.setLineWrapMode(QtGui.QPlainTextEdit.WidgetWidth if self.preferences['wordWrap'] else QtGui.QPlainTextEdit.NoWrap)


    def onActionHomepage(self):
        url = QtCore.QUrl('http://foosoft.net/projects/yomichan')
        QtGui.QDesktopServices().openUrl(url)


    def onActionFeedback(self):
        url = QtCore.QUrl('http://foosoft.net/about')
        QtGui.QDesktopServices().openUrl(url)


    def onVocabDefsAnchorClicked(self, url):
        command, index = unicode(url.toString()).split(':')
        self.executeVocabCommand(command, int(index))


    def onKanjiDefsAnchorClicked(self, url):
        command, index = unicode(url.toString()).split(':')
        self.executeKanjiCommand(command, int(index))


    def onVocabDefSearchReturn(self):
        text = unicode(self.textVocabSearch.text())
        self.state.vocabDefs, length = self.language.findTerm(text, True)
        self.updateVocabDefs()
        if self.dockKanji.isVisible():
            self.state.kanjiDefs = self.language.findCharacters(text)
            self.updateKanjiDefs()


    def onKanjiDefSearchReturn(self):
        text = unicode(self.textKanjiSearch.text())
        self.state.kanjiDefs = self.language.findCharacters(text)
        self.updateKanjiDefs()


    def onDefinitionDoubleClicked(self, item):
        profile = self.preferences['profiles'].get('vocab')
        if profile is not None and self.anki is not None:
            key = self.anki.getModelKey(profile['model'])
            row = self.listDefinitions.row(item)
            self.anki.browse({key:self.facts[row],u'note':profile['model']})


    def onVisibilityChanged(self, visible):
        self.actionToggleAnki.setChecked(self.dockAnki.isVisible())
        self.actionToggleVocab.setChecked(self.dockVocab.isVisible())
        self.actionToggleKanji.setChecked(self.dockKanji.isVisible())


    def onUpdaterSearchResult(self, versions):
        if versions['latest'] > constants.c['appVersion']:
            dialog = updates.DialogUpdates(self, versions)
            dialog.exec_()


    def onContentMouseMove(self, event):
        QtGui.QPlainTextEdit.mouseMoveEvent(self.textContent, event)
        self.updateSampleMouseEvent(event)


    def onContentMousePress(self, event):
        QtGui.QPlainTextEdit.mousePressEvent(self.textContent, event)
        self.updateSampleMouseEvent(event)


    def openFile(self, filename):
        filename = unicode(filename)
        self.closeFile()
        try:
            self.currentFile = FileState(filename, self.preferences['stripReadings'])
        except IOError:
            self.setStatus(u'Failed to load file {0}'.format(filename))
            QtGui.QMessageBox.critical(self, 'Yomichan', 'Cannot open file for read')
            return
        self.listDefinitions.clear()
        self.facts = []

        self.updateRecentFile()
        self.updateRecentFiles()

        allCards = self.plugin.fetchAllCards()
        if allCards is not None:
            self.currentFile.findVocabulary(self.anki.collection().sched,allCards)
            # if file contains exported vocabs, create the cards
            if self.currentFile.exportedVocab:
                for notFound in self.currentFile.wordsNotFound:
                    self.ankiAddFact('vocab',self.currentFile.wordsMarkup[notFound],addToList=False)
            for word,card in self.currentFile.wordsAll.items():
                self.facts.append(word)
                self.listDefinitions.addItem(word)
            self.listDefinitions.setCurrentRow(self.listDefinitions.count() - 1)

        content = self.currentFile.content
        self.state.filename = filename
        self.state.scanPosition = self.preferences.filePosition(filename)
        if self.state.scanPosition > len(content):
            self.state.scanPosition = 0
        self.textContent.setPlainText(content)
        if self.state.scanPosition > 0:
            cursor = self.textContent.textCursor()
            cursor.setPosition(self.state.scanPosition)
            self.textContent.setTextCursor(cursor)
            self.textContent.centerCursor()
                          

        self.setWindowTitle(u'Yomichan - {0} ({1})'.format(os.path.basename(filename), self.currentFile.encoding))
        self.setStatus(u'Loaded file {0}'.format(filename))

    def saveFile(self, filename):
        try:
            filename = unicode(filename)
            with open(filename,'w') as fp:
                content = self.textContent.toPlainText()
                content+= self.currentFile.getExportVocabularyList(preferences.exportAllowedTags['vocab'])
                fp.write(content.encode('utf-8'))
                fp.close()
        except IOError:
            self.setStatus(u'Failed to save file {0}'.format(filename))
            QtGui.QMessageBox.critical(self, 'Yomichan', 'Cannot open file for write')
            return
        self.state.filename = filename
        self.currentFile.filename = filename
        self.updateRecentFile()
        self.updateRecentFiles()
        self.setWindowTitle(u'Yomichan - {0} ({1})'.format(os.path.basename(filename), 'utf-8'))

    def closeFile(self):
        if self.preferences['rememberTextContent']:
            self.preferences['textContent'] = unicode(self.textContent.toPlainText())

        self.setWindowTitle('Yomichan')
        self.textContent.setPlainText(unicode())
        self.updateRecentFile(False)
        self.state = self.State()


    def findText(self, text):
        content = unicode(self.textContent.toPlainText())
        index = content.find(unicode(text), self.state.searchPosition)

        if index == -1:
            wrap = self.state.searchPosition != 0
            self.state.searchPosition = 0
            if wrap:
                self.findText(text)
            else:
                QtGui.QMessageBox.information(self, 'Yomichan', 'Search text not found')
        else:
            self.state.searchPosition = index + len(text)
            cursor = self.textContent.textCursor()
            cursor.setPosition(index, QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(self.state.searchPosition, QtGui.QTextCursor.KeepAnchor)
            self.textContent.setTextCursor(cursor)

        self.state.searchText = text

    def ankiOverwriteFact(self, profile, markup):
        if markup is None:
            return False

        if self.anki is None:
            return False

        profile = self.preferences['profiles'].get(profile)
        if profile is None:
            return False
        
        fields = reader_util.formatFields(profile['fields'], markup)
        tagsSplit = reader_util.splitTags(unicode(self.comboTags.currentText()))
        tagsJoined = ' '.join(tagsSplit)

        tagIndex = self.comboTags.findText(tagsJoined)
        if tagIndex > 0:
            self.comboTags.removeItem(tagIndex)
        if tagIndex != 0:
            self.comboTags.insertItem(0, tagsJoined)
        self.preferences.updateFactTags(tagsJoined)

        key = self.anki.getModelKey(profile['model'])                                                  
        value = fields[key]
        ids = self.anki.getNotes(profile['model'],key,value)
        if len(ids) == 0:
            return False
        
        # Overwrite the fields in the note
        # or add a line, if a + is at the end of field name
        note = self.anki.collection().getNote(ids[0])   
        for name, v in fields.items():
            if name in note:
                if unicode(name[-1]) == u'+' and len(note[name])>0:
                    note[name]+= u'<br>' + v
                else:
                    note[name] = v 
        note.flush()
        
        self.freshlyAdded.append(value)
        cids = self.anki.getCardsByNote(profile['model'],key,value)
        if len(cids) == 0:
            return False
        self.currentFile.overwriteVocabulary(value,self.anki.collection().getCard(cids[0]))
        self.currentFile.addMarkup(value,markup)
        self.facts.append(value)
        self.listDefinitions.addItem(value)
        self.listDefinitions.setCurrentRow(self.listDefinitions.count() - 1)
        self.updateVocabDefs(scroll=True)
        self.updateKanjiDefs(scroll=True)
        return True

    def ankiAddFact(self, profile, markup, addToList = True):
        if markup is None:
            return False

        if self.anki is None:
            return False

        profile = self.preferences['profiles'].get(profile)
        if profile is None:
            return False

        fields = reader_util.formatFields(profile['fields'], markup)
        fld = [(x,y) for x,y in fields.items() if x in ['v','Vocabulary-Furigana']]
        tagsSplit = reader_util.splitTags(unicode(self.comboTags.currentText()))
        tagsJoined = ' '.join(tagsSplit)

        tagIndex = self.comboTags.findText(tagsJoined)
        if tagIndex > 0:
            self.comboTags.removeItem(tagIndex)
        if tagIndex != 0:
            self.comboTags.insertItem(0, tagsJoined)
        self.preferences.updateFactTags(tagsJoined)

        factId = self.anki.addNote(profile['deck'], profile['model'], fields, tagsSplit)
        if factId is None:
            return False
            
        key = self.anki.getModelKey(profile['model'])
        value = fields[key]
        # Put the vocabulary out of 'new' state and add it to the vocabulary list
        ids = self.anki.getCardsByNote(profile['model'],key,value)
        if len(ids) == 0:
            return False
        card = self.anki.collection().getCard(ids[0])
        self.freshlyAdded.append(value)
        self.currentFile.addVocabulary(value,card,addToBadListToo = False)
        self.currentFile.addMarkup(value,markup)
        if self.preferences['unlockVocab']:
            self.anki.collection().sched.earlyAnswerCard(card,2)
        if addToList:
            self.facts.append(value)
            self.listDefinitions.addItem(value)
            self.listDefinitions.setCurrentRow(self.listDefinitions.count() - 1)
        self.setStatus(u'Added fact {0}; {1} new fact(s) total'.format(markup['summary'], len(self.facts)))

        self.updateVocabDefs(scroll=True)
        self.updateKanjiDefs(scroll=True)
        return True


    def ankiIsFactValid(self, prfl, markup, index):
        if markup is None:
            return False

        if self.anki is None:
            return False

        profile = self.preferences['profiles'].get('vocab' if prfl[:5] == 'vocab' else prfl)
        if profile is None:
            return False

        fields = reader_util.formatFields(profile['fields'], markup)
        if prfl[:5] == 'vocab':
            key = self.anki.getModelKey(profile['model'])
            if self.longestMatch is None:
                self.longestMatch = index
            if key is not None and fields[key] in self.currentFile.wordsAll:
                if len(fields[key]) > len(self.longestMatchKey):
                    self.longestMatch = index
                    self.longestMatchKey = fields[key]

        result = self.anki.canAddNote(profile['deck'], profile['model'], fields)
        
        if 0 <= index < 10:
            if prfl == 'vocab':
                self.overwritable[index] = not result
            elif prfl == 'vocabReading':
                self.overwritableReading[index] = not result
                
        return result


    def executeVocabCommand(self, command, index):
        if index >= len(self.state.vocabDefs):
            return

        definition = self.state.vocabDefs[index]
        if command == 'addVocabExp':
            markup = reader_util.markupVocabExp(definition)
            self.ankiAddFact('vocab', markup)
        elif command == 'overwriteVocabExp':
            markup = reader_util.markupVocabExp(definition)
            self.ankiOverwriteFact('vocab', markup)            
        elif command == 'addVocabReading':
            markup = reader_util.markupVocabReading(definition)
            self.ankiAddFact('vocab', markup)
        elif command == 'overwriteVocabReading':
            markup = reader_util.markupVocabReading(definition)
            self.ankiOverwriteFact('vocab', markup)
        elif command == 'copyVocabDef':
            reader_util.copyVocabDef(definition)


    def executeKanjiCommand(self, command, index):
        if index >= len(self.state.kanjiDefs):
            return

        definition = self.state.kanjiDefs[index]
        if command == 'addKanji':
            markup = reader_util.markupKanji(definition)
            self.ankiAddFact('kanji', markup)
        elif command == 'copyKanjiDef':
            reader_util.copyKanjiDef(definition)


    def updateSampleMouseEvent(self, event):
        cursor = self.textContent.cursorForPosition(event.pos())
        self.state.scanPosition = cursor.position()
        if event.buttons() & QtCore.Qt.MidButton or event.modifiers() & QtCore.Qt.ShiftModifier:
            self.updateSampleFromPosition()


    def updateSampleFromPosition(self):
        samplePosStart = self.state.scanPosition
        samplePosEnd = self.state.scanPosition + self.preferences['scanLength']

        cursor = self.textContent.textCursor()
        content = unicode(self.textContent.toPlainText())
        contentSample = content[samplePosStart:samplePosEnd]
        contentSampleFlat = contentSample.replace(u'\n', unicode())

        if len(contentSampleFlat) == 0 or not japanese.util.isJapanese(contentSampleFlat[0]):
            cursor.clearSelection()
            self.textContent.setTextCursor(cursor)
            return

        lengthMatched = 0
        if self.dockVocab.isVisible():
            self.state.vocabDefs, lengthMatched = self.language.findTerm(contentSampleFlat)
            sentence, line = reader_util.findSentence(content, samplePosStart)
            for definition in self.state.vocabDefs:
                definition['sentence'] = sentence
                definition['line'] = line
                definition['filename'] = self.state.filename
            self.updateVocabDefs()

        if self.dockKanji.isVisible():
            if lengthMatched == 0:
                self.state.kanjiDefs = self.language.findCharacters(contentSampleFlat[0])
                if len(self.state.kanjiDefs) > 0:
                    lengthMatched = 1
            else:
                self.state.kanjiDefs = self.language.findCharacters(contentSampleFlat[:lengthMatched])
            self.updateKanjiDefs()

        lengthSelect = 0
        for c in contentSample:
            if lengthMatched <= 0:
                break
            lengthSelect += 1
            if c != u'\n':
                lengthMatched -= 1

        cursor.setPosition(samplePosStart, QtGui.QTextCursor.MoveAnchor)
        cursor.setPosition(samplePosStart + lengthSelect, QtGui.QTextCursor.KeepAnchor)
        self.textContent.setTextCursor(cursor)


    def clearRecentFiles(self):
        self.preferences.clearRecentFiles()
        self.updateRecentFiles()


    def updateRecentFiles(self):
        self.menuOpenRecent.clear()

        filenames = self.preferences.recentFiles()
        if len(filenames) == 0:
            return

        for filename in filenames:
            self.menuOpenRecent.addAction(filename, lambda f=filename: self.openFile(f))

        self.menuOpenRecent.addSeparator()
        self.menuOpenRecent.addAction('Clear file history', self.clearRecentFiles)


    def updateRecentFile(self, addIfNeeded=True):
        if self.state.filename:
            if addIfNeeded or self.state.filename in self.preferences.recentFiles():
                self.preferences.updateRecentFile(self.state.filename, self.state.scanPosition)


    def updateDefs(self, defs, builder, control, **options):
        if options.get('trim', True):
            defs = defs[:self.preferences['maxResults']]

        html = builder(defs, self.ankiIsFactValid, self.anki is not None)
        
        scrollbar = control.verticalScrollBar()
        position = scrollbar.sliderPosition()
        control.setHtml(html)

        if options.get('scroll', False):
            scrollbar.setSliderPosition(position)


    def updateVocabDefs(self, **options):
        self.longestMatch = None
        self.longestMatchKey = u''
        self.updateDefs(
            self.state.vocabDefs,
            reader_util.buildVocabDefs,
            self.textVocabDefs,
            **options
        )
        if self.currentFile is not None:
            # User had to look up the word, put it into the wrong list
            if self.longestMatchKey in self.currentFile.wordsAll:
                if self.longestMatchKey in self.freshlyAdded:
                    self.freshlyAdded.remove(self.longestMatchKey)
                else:
                    self.currentFile.wordsBad[self.longestMatchKey] = self.currentFile.wordsAll[self.longestMatchKey]
                    self.setStatus(u'{0} has been put into the incorrectly answered set'.format(self.longestMatchKey))


    def updateKanjiDefs(self, **options):
        self.updateDefs(
            self.state.kanjiDefs,
            reader_util.buildKanjiDefs,
            self.textKanjiDefs,
            **options
        )


    def importWordList(self, words):
        self.state.vocabDefs = list()
        self.state.kanjiDefs = list()

        for word in words:
            if self.dockVocab.isVisible():
                self.state.vocabDefs += self.language.dictionary.findTerm(word)

            if self.dockKanji.isVisible():
                self.state.kanjiDefs += self.language.findCharacters(word)

        self.updateVocabDefs(trim=False, scroll=True)
        self.updateKanjiDefs(trim=False, scroll=True)


    def setStatus(self, status):
        self.statusBar.showMessage(status)
