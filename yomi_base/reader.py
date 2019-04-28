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
import os
import preferences
import reader_util
import updates


class MainWindowReader(QtGui.QMainWindow, gen.reader_ui.Ui_MainWindowReader):
    class State:
        def __init__(self):
            self.filename       = u''
            self.searchText     = u''
            self.kanjiDefs      = []
            self.vocabDefs      = []
            self.scanPosition   = 0
            self.searchPosition = 0


    def __init__(self, parent, preferences, language, filename=None, anki=None, closed=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.textContent.mouseMoveEvent  = self.onContentMouseMove
        self.textContent.mousePressEvent = self.onContentMousePress
        self.dockAnki.setEnabled(anki is not None)

        self.facts       = []
        self.anki        = anki
        self.closed      = closed
        self.language    = language
        self.preferences = preferences
        self.state       = self.State()
        self.updates     = updates.UpdateFinder()
        self.zoom        = 0

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

        self.actionAbout.triggered.connect(self.onActionAbout)
        self.actionFind.triggered.connect(self.onActionFind)
        self.actionFindNext.triggered.connect(self.onActionFindNext)
        self.actionHomepage.triggered.connect(self.onActionHomepage)
        self.actionKindleDeck.triggered.connect(self.onActionKindleDeck)
        self.actionWordList.triggered.connect(self.onActionWordList)
        self.actionOpen.triggered.connect(self.onActionOpen)
        self.actionPreferences.triggered.connect(self.onActionPreferences)
        self.actionToggleWrap.toggled.connect(self.onActionToggleWrap)
        self.actionZoomIn.triggered.connect(self.onActionZoomIn)
        self.actionZoomOut.triggered.connect(self.onActionZoomOut)
        self.actionZoomReset.triggered.connect(self.onActionZoomReset)
        self.dockAnki.visibilityChanged.connect(self.onVisibilityChanged)
        self.dockKanji.visibilityChanged.connect(self.onVisibilityChanged)
        self.dockVocab.visibilityChanged.connect(self.onVisibilityChanged)
        self.listDefinitions.itemDoubleClicked.connect(self.onDefinitionDoubleClicked)
        self.textKanjiDefs.anchorClicked.connect(self.onKanjiDefsAnchorClicked)
        self.textKanjiSearch.returnPressed.connect(self.onKanjiDefSearchReturn)
        self.textVocabDefs.anchorClicked.connect(self.onVocabDefsAnchorClicked)
        self.textVocabSearch.returnPressed.connect(self.onVocabDefSearchReturn)
        self.updates.updateResult.connect(self.onUpdaterSearchResult)

        if self.preferences['checkForUpdates']:
            self.updates.start()


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
                'This may be the first time you are running Yomichan.\n' \
                'Please take some time to configure this extension.'
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
        elif ord('0') <= event.key() <= ord('9'):
            index = event.key() - ord('0') - 1
            if index < 0:
                index = 9
            if event.modifiers() & QtCore.Qt.ShiftModifier:
                if event.modifiers() & QtCore.Qt.ControlModifier:
                    self.executeKanjiCommand('addKanji', index)
            else:
                if event.modifiers() & QtCore.Qt.ControlModifier:
                    self.executeVocabCommand('addVocabExp', index)
                if event.modifiers() & QtCore.Qt.AltModifier:
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
            filter='Text files (*.txt);;All files (*.*)'
        )
        if filename:
            self.openFile(filename)


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
        mode = QtGui.QPlainTextEdit.WidgetWidth if self.preferences['wordWrap'] else QtGui.QPlainTextEdit.NoWrap
        self.textContent.setLineWrapMode(mode)


    def onActionHomepage(self):
        url = QtCore.QUrl('https://foosoft.net/projects/yomichan')
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
            self.state.kanjiDefs = self.language.findKanji(text)
            self.updateKanjiDefs()


    def onKanjiDefSearchReturn(self):
        text = unicode(self.textKanjiSearch.text())
        self.state.kanjiDefs = self.language.findKanji(text)
        self.updateKanjiDefs()


    def onDefinitionDoubleClicked(self, item):
        if self.anki is not None:
            row = self.listDefinitions.row(item)
            self.anki.browseNote(self.facts[row])


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
        try:
            filename = unicode(filename)
            with open(filename) as fp:
                content = fp.read()
        except IOError:
            self.setStatus(u'Failed to load file {0}'.format(filename))
            QtGui.QMessageBox.critical(self, 'Yomichan', 'Cannot open file for read')
            return

        self.closeFile()

        self.state.filename = filename
        self.state.scanPosition = self.preferences.filePosition(filename)
        if self.state.scanPosition > len(content):
            self.state.scanPosition = 0

        self.updateRecentFile()
        self.updateRecentFiles()

        content, encoding = reader_util.decodeContent(content)
        if self.preferences['stripReadings']:
            content = reader_util.stripReadings(content)

        self.textContent.setPlainText(content)
        if self.state.scanPosition > 0:
            cursor = self.textContent.textCursor()
            cursor.setPosition(self.state.scanPosition)
            self.textContent.setTextCursor(cursor)
            self.textContent.centerCursor()

        self.setStatus(u'Loaded file {0}'.format(filename))
        self.setWindowTitle(u'Yomichan - {0} ({1})'.format(os.path.basename(filename), encoding))


    def closeFile(self):
        if self.preferences['rememberTextContent']:
            self.preferences['textContent'] = unicode(self.textContent.toPlainText())

        self.setWindowTitle('Yomichan')
        self.textContent.setPlainText(u'')
        self.updateRecentFile(False)
        self.state = self.State()


    def findText(self, text):
        content = unicode(self.textContent.toPlainText())
        index   = content.find(unicode(text), self.state.searchPosition)

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


    def ankiAddFact(self, profile, markup):
        if markup is None:
            return False

        if self.anki is None:
            return False

        profile = self.preferences['profiles'].get(profile)
        if profile is None:
            return False

        fields     = reader_util.formatFields(profile['fields'], markup)
        tagsSplit  = reader_util.splitTags(unicode(self.comboTags.currentText()))
        tagsJoined = ' '.join(tagsSplit)

        tagIndex = self.comboTags.findText(tagsJoined)
        if tagIndex > 0:
            self.comboTags.removeItem(tagIndex)
        if tagIndex != 0:
            self.comboTags.insertItem(0, tagsJoined)
        self.preferences.updateFactTags(tagsJoined)

        factId = self.anki.addNote(profile['deck'], profile['model'], fields, tagsSplit, None)
        if factId is None:
            return False

        self.facts.append(factId)
        self.listDefinitions.addItem(markup['summary'])
        self.listDefinitions.setCurrentRow(self.listDefinitions.count() - 1)
        self.setStatus(u'Added fact {0}; {1} new fact(s) total'.format(markup['summary'], len(self.facts)))

        self.updateVocabDefs(scroll=True)
        self.updateKanjiDefs(scroll=True)
        return True


    def ankiIsFactValid(self, profile, markup):
        if markup is None:
            return False

        if self.anki is None:
            return False

        profile = self.preferences['profiles'].get(profile)
        if profile is None:
            return False

        fields = reader_util.formatFields(profile['fields'], markup)
        return self.anki.canAddNote(profile['deck'], profile['model'], fields)


    def executeVocabCommand(self, command, index):
        if index >= len(self.state.vocabDefs):
            return

        definition = self.state.vocabDefs[index]
        if command == 'addVocabExp':
            markup = reader_util.markupVocabExp(definition)
            self.ankiAddFact('vocab', markup)
        if command == 'addVocabReading':
            markup = reader_util.markupVocabReading(definition)
            self.ankiAddFact('vocab', markup)
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
        samplePosEnd   = self.state.scanPosition + self.preferences['scanLength']

        content           = unicode(self.textContent.toPlainText())
        contentSample     = content[samplePosStart:samplePosEnd]
        contentSampleFlat = contentSample.replace(u'\n', u'')

        cursor = self.textContent.textCursor()

        if len(contentSampleFlat) == 0:
            cursor.clearSelection()
            self.textContent.setTextCursor(cursor)
            return

        lengthMatched = 0
        if self.dockVocab.isVisible():
            self.state.vocabDefs, lengthMatched = self.language.findTerm(contentSampleFlat)
            sentence = reader_util.findSentence(content, samplePosStart)
            for definition in self.state.vocabDefs:
                definition['sentence'] = sentence
            self.updateVocabDefs()

        if self.dockKanji.isVisible():
            if lengthMatched == 0:
                self.state.kanjiDefs = self.language.findKanji(contentSampleFlat[0])
                if len(self.state.kanjiDefs) > 0:
                    lengthMatched = 1
            else:
                self.state.kanjiDefs = self.language.findKanji(contentSampleFlat[:lengthMatched])
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
        scrollbar = control.verticalScrollBar()
        position  = scrollbar.sliderPosition()

        html = builder(defs, self.ankiIsFactValid)
        control.setHtml(html)

        if options.get('scroll', False):
            scrollbar.setSliderPosition(position)


    def updateVocabDefs(self, **options):
        self.updateDefs(
            self.state.vocabDefs,
            reader_util.buildVocabDefs,
            self.textVocabDefs,
            **options
        )


    def updateKanjiDefs(self, **options):
        self.updateDefs(
            self.state.kanjiDefs,
            reader_util.buildKanjiDefs,
            self.textKanjiDefs,
            **options
        )


    def importWordList(self, words):
        self.state.vocabDefs = []
        self.state.kanjiDefs = []

        for word in words:
            if self.dockVocab.isVisible():
                self.state.vocabDefs += self.language.dictionary.findTerm(word)

            if self.dockKanji.isVisible():
                self.state.kanjiDefs += self.language.findKanji(word)

        self.updateVocabDefs(scroll=True)
        self.updateKanjiDefs(scroll=True)


    def setStatus(self, status):
        self.statusBar.showMessage(status)
