# -*- coding: utf-8 -*-

# Copyright (C) 2011  Alex Yatskov
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


import os
from xml.dom import minidom
from PyQt4 import QtCore, QtGui


class Preferences:
    def __init__(self):
        self.clear()


    def clear(self):
        self.generalFindUpdates = True
        self.generalReadingsStrip = False
        self.generalRecentLoad = True
        self.generalRecentFiles = list()
        self.generalRecentMax = 10

        self.uiContentFontFamily = 'Arial'
        self.uiContentFontSize = 12
        self.uiContentColorFg = QtGui.QColor(QtCore.Qt.black).rgba()
        self.uiContentColorBg = QtGui.QColor(QtCore.Qt.white).rgba()
        self.uiContentWordWrap = False

        self.uiReaderState = None
        self.uiReaderPosition = None
        self.uiReaderSize = None

        self.searchScanMax = 16
        self.searchResultMax = 32
        self.searchGroupByExp = True

        self.ankiFields = dict()
        self.ankiTags = list()
        self.ankiDeck = unicode()
        self.ankiModel = unicode()


    def load(self, filename=None):
        if not filename:
            filename = self.defaultFilename()

        try:
            doc = minidom.parse(filename)
        except:
            return False

        root = doc.documentElement
        if root.nodeName != 'yomichan':
            return False

        self.clear()

        for general in root.getElementsByTagName('general'):
            self.generalRecentLoad = self.readAttrBool(general, 'recentLoad', self.generalRecentLoad)
            self.generalReadingsStrip = self.readAttrBool(general, 'readingsStrip', self.generalReadingsStrip)
            self.generalFindUpdates = self.readAttrBool(general, 'findUpdates', self.generalFindUpdates)

            for recent in general.getElementsByTagName('recent'):
                path = self.readAttrStr(recent, 'path')
                position = self.readAttrInt(recent, 'position')
                if path and os.path.isfile(path):
                    self.generalRecentFiles.append((path, position))

        for ui in root.getElementsByTagName('ui'):
            for content in ui.getElementsByTagName('content'):
                self.uiContentFontFamily = self.readAttrStr(content, 'fontFamily', self.uiContentFontFamily)
                self.uiContentFontSize = self.readAttrInt(content, 'fontSize', self.uiContentFontSize)
                self.uiContentColorFg = self.readAttrInt(content, 'colorFg', self.uiContentColorFg)
                self.uiContentColorBg = self.readAttrInt(content, 'colorBg', self.uiContentColorBg)
                self.uiContentWordWrap = self.readAttrBool(content, 'wordWrap', self.uiContentWordWrap)

            for reader in ui.getElementsByTagName('reader'):
                self.uiReaderState = self.readAttrStr(reader, 'state', self.uiReaderState)
                self.uiReaderPosition = self.readAttrIntTuple(reader, 'position', self.uiReaderPosition)
                self.uiReaderSize = self.readAttrIntTuple(reader, 'size', self.uiReaderSize)

        for search in root.getElementsByTagName('search'):
            self.searchScanMax = self.readAttrInt(search, 'scanMax', self.searchScanMax)
            self.searchResultMax = self.readAttrInt(search, 'resultMax', self.searchResultMax)
            self.searchGroupByExp = self.readAttrBool(search, 'groupByExp', self.searchGroupByExp)

        for anki in root.getElementsByTagName('anki'):
            self.ankiDeck = self.readAttrStr(anki, 'deck', unicode())
            self.ankiModel = self.readAttrStr(anki, 'model', unicode())

            for tag in anki.getElementsByTagName('tag'):
                value = self.readAttrStr(tag, 'value', unicode())
                self.ankiTags.append(value)

            for model in anki.getElementsByTagName('model'):
                for field in model.getElementsByTagName('field'):
                    name = self.readAttrStr(field, 'name')
                    value = self.readAttrStr(field, 'value')
                    if name and value:
                        self.ankiFields[name] = value

        return True


    def save(self, filename=None):
        if not filename:
            filename = self.defaultFilename()

        directory = os.path.split(filename)[0]
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError:
                return False

        doc = minidom.Document()
        root = doc.createElement('yomichan')
        doc.appendChild(root)

        general = doc.createElement('general')
        root.appendChild(general)
        self.writeAttrBool(general, 'recentLoad', self.generalRecentLoad)
        self.writeAttrBool(general, 'readingsStrip', self.generalReadingsStrip)
        self.writeAttrBool(general, 'findUpdates', self.generalFindUpdates)
        for path, position in self.generalRecentFiles:
            recent = doc.createElement('recent')
            general.appendChild(recent)
            self.writeAttrStr(recent, 'path', path)
            self.writeAttrInt(recent, 'position', position)

        ui = doc.createElement('ui')
        root.appendChild(ui)

        content = doc.createElement('content')
        ui.appendChild(content)
        self.writeAttrStr(content, 'fontFamily', self.uiContentFontFamily)
        self.writeAttrInt(content, 'fontSize', self.uiContentFontSize)
        self.writeAttrInt(content, 'colorFg', self.uiContentColorFg)
        self.writeAttrInt(content, 'colorBg', self.uiContentColorBg)
        self.writeAttrBool(content, 'wordWrap', self.uiContentWordWrap)

        reader = doc.createElement('reader')
        ui.appendChild(reader)
        self.writeAttrStr(reader, 'state', self.uiReaderState)
        self.writeAttrIntTuple(reader, 'position', self.uiReaderPosition)
        self.writeAttrIntTuple(reader, 'size', self.uiReaderSize)

        search = doc.createElement('search')
        root.appendChild(search)
        self.writeAttrInt(search, 'scanMax', self.searchScanMax)
        self.writeAttrInt(search, 'resultMax', self.searchResultMax)
        self.writeAttrBool(search, 'groupByExp', self.searchGroupByExp)

        anki = doc.createElement('anki')
        root.appendChild(anki)
        self.writeAttrStr(anki, 'deck', self.ankiDeck)
        self.writeAttrStr(anki, 'model', self.ankiModel)

        for value in self.ankiTags:
            tag = doc.createElement('tag')
            anki.appendChild(tag)
            self.writeAttrStr(tag, 'value', value)

        if self.ankiFields:
            model = doc.createElement('model')
            anki.appendChild(model)
            for name, value in self.ankiFields.items():
                field = doc.createElement('field')
                model.appendChild(field)
                self.writeAttrStr(field, 'name', name)
                self.writeAttrStr(field, 'value', value)

        try:
            with open(filename, 'w') as fp:
                fp.write(doc.toprettyxml(encoding='utf-8'))
        except IOError:
            return False

        return True


    def defaultFilename(self):
        return os.path.expanduser('~/.yomichan/preferences.xml')


    def filePosition(self, filename):
        results = filter(lambda x: x[0] == filename, self.generalRecentFiles)
        return results[0][1] if results else 0


    def recentFiles(self):
        return map(lambda x: x[0], self.generalRecentFiles)


    def updateFactTags(self, tags):
        if tags in self.ankiTags:
            self.ankiTags.remove(tags)
        self.ankiTags.insert(0, tags)


    def updateRecentFile(self, filename, position):
        self.generalRecentFiles = filter(lambda x: x[0] != filename, self.generalRecentFiles)
        self.generalRecentFiles.insert(0, (filename, position))
        self.generalRecentFiles = self.generalRecentFiles[:self.generalRecentMax]


    def clearRecentFiles(self):
        self.generalRecentFiles = list()


    def readAttrStr(self, node, name, default=None):
        return node.getAttribute(name) or default


    def readAttrBool(self, node, name, default=False):
        value = self.readAttrStr(node, name)
        return value.lower() == 'true' if value else default


    def readAttrInt(self, node, name, default=0):
        value = self.readAttrStr(node, name)
        return int(value) if value else default


    def readAttrIntTuple(self, node, name, default=None):
        value = self.readAttrStr(node, name)
        return tuple([int(v) for v in value.split(',')]) if value else default


    def writeAttrStr(self, node, name, value):
        if value != None:
            node.setAttribute(name, value)


    def writeAttrBool(self, node, name, value):
        if value != None:
            node.setAttribute(name, ['false', 'true'][bool(value)])


    def writeAttrInt(self, node, name, value):
        if value != None:
            node.setAttribute(name, str(value))


    def writeAttrIntTuple(self, node, name, value):
        if value != None:
            node.setAttribute(name, ','.join([str(v) for v in value]))
