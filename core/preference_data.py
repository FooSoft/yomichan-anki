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
        self.ankiShowIcon = True


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
            self.generalRecentLoad = self.__readAttrBool(general, 'recentLoad', self.generalRecentLoad)
            self.generalReadingsStrip = self.__readAttrBool(general, 'readingsStrip', self.generalReadingsStrip)
            self.generalFindUpdates = self.__readAttrBool(general, 'findUpdates', self.generalFindUpdates)

            for recent in general.getElementsByTagName('recent'):
                path = self.__readAttrStr(recent, 'path')
                position = self.__readAttrInt(recent, 'position')
                if path and os.path.isfile(path):
                    self.generalRecentFiles.append((path, position))

        for ui in root.getElementsByTagName('ui'):
            for content in ui.getElementsByTagName('content'):
                self.uiContentFontFamily = self.__readAttrStr(content, 'fontFamily', self.uiContentFontFamily)
                self.uiContentFontSize = self.__readAttrInt(content, 'fontSize', self.uiContentFontSize)
                self.uiContentColorFg = self.__readAttrInt(content, 'colorFg', self.uiContentColorFg)
                self.uiContentColorBg = self.__readAttrInt(content, 'colorBg', self.uiContentColorBg)
                self.uiContentWordWrap = self.__readAttrBool(content, 'wordWrap', self.uiContentWordWrap)

            for reader in ui.getElementsByTagName('reader'):
                self.uiReaderState = self.__readAttrStr(reader, 'state', self.uiReaderState)
                self.uiReaderPosition = self.__readAttrIntTuple(reader, 'position', self.uiReaderPosition)
                self.uiReaderSize = self.__readAttrIntTuple(reader, 'size', self.uiReaderSize)

        for search in root.getElementsByTagName('search'):
            self.searchScanMax = self.__readAttrInt(search, 'scanMax', self.searchScanMax)
            self.searchResultMax = self.__readAttrInt(search, 'resultMax', self.searchResultMax)
            self.searchGroupByExp = self.__readAttrBool(search, 'groupByExp', self.searchGroupByExp)

        for anki in root.getElementsByTagName('anki'):
            self.ankiShowIcon = self.__readAttrBool(anki, 'showIcon', self.ankiShowIcon)

            for tag in anki.getElementsByTagName('tag'):
                value = self.__readAttrStr(tag, 'value', unicode())
                self.ankiTags.append(value)

            for model in anki.getElementsByTagName('model'):
                for field in model.getElementsByTagName('field'):
                    name = self.__readAttrStr(field, 'name')
                    value = self.__readAttrStr(field, 'value')
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
        self.__writeAttrBool(general, 'recentLoad', self.generalRecentLoad)
        self.__writeAttrBool(general, 'readingsStrip', self.generalReadingsStrip)
        self.__writeAttrBool(general, 'findUpdates', self.generalFindUpdates)
        for path, position in self.generalRecentFiles:
            recent = doc.createElement('recent')
            general.appendChild(recent)
            self.__writeAttrStr(recent, 'path', path)
            self.__writeAttrInt(recent, 'position', position)

        ui = doc.createElement('ui')
        root.appendChild(ui)

        content = doc.createElement('content')
        ui.appendChild(content)
        self.__writeAttrStr(content, 'fontFamily', self.uiContentFontFamily)
        self.__writeAttrInt(content, 'fontSize', self.uiContentFontSize)
        self.__writeAttrInt(content, 'colorFg', self.uiContentColorFg)
        self.__writeAttrInt(content, 'colorBg', self.uiContentColorBg)
        self.__writeAttrBool(content, 'wordWrap', self.uiContentWordWrap)

        reader = doc.createElement('reader')
        ui.appendChild(reader)
        self.__writeAttrStr(reader, 'state', self.uiReaderState)
        self.__writeAttrIntTuple(reader, 'position', self.uiReaderPosition)
        self.__writeAttrIntTuple(reader, 'size', self.uiReaderSize)

        search = doc.createElement('search')
        root.appendChild(search)
        self.__writeAttrInt(search, 'scanMax', self.searchScanMax)
        self.__writeAttrInt(search, 'resultMax', self.searchResultMax)
        self.__writeAttrBool(search, 'groupByExp', self.searchGroupByExp)

        anki = doc.createElement('anki')
        root.appendChild(anki)
        self.__writeAttrBool(anki, 'showIcon', self.ankiShowIcon)

        for value in self.ankiTags:
            tag = doc.createElement('tag')
            anki.appendChild(tag)
            self.__writeAttrStr(tag, 'value', value)

        if self.ankiFields:
            model = doc.createElement('model')
            anki.appendChild(model)
            for name, value in self.ankiFields.items():
                field = doc.createElement('field')
                model.appendChild(field)
                self.__writeAttrStr(field, 'name', name)
                self.__writeAttrStr(field, 'value', value)

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


    def __readAttrStr(self, node, name, default=None):
        return node.getAttribute(name) or default


    def __readAttrBool(self, node, name, default=False):
        value = self.__readAttrStr(node, name)
        return value.lower() == 'true' if value else default


    def __readAttrInt(self, node, name, default=0):
        value = self.__readAttrStr(node, name)
        return int(value) if value else default


    def __readAttrIntTuple(self, node, name, default=None):
        value = self.__readAttrStr(node, name)
        return tuple([int(v) for v in value.split(',')]) if value else default


    def __writeAttrStr(self, node, name, value):
        if value != None:
            node.setAttribute(name, value)


    def __writeAttrBool(self, node, name, value):
        if value != None:
            node.setAttribute(name, ['false', 'true'][bool(value)])


    def __writeAttrInt(self, node, name, value):
        if value != None:
            node.setAttribute(name, str(value))


    def __writeAttrIntTuple(self, node, name, value):
        if value != None:
            node.setAttribute(name, ','.join([str(v) for v in value]))
