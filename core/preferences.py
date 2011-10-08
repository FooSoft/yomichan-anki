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


from PyQt4 import QtGui, QtCore
from preferences_ui import Ui_DialogPreferences


class DialogPreferences(QtGui.QDialog, Ui_DialogPreferences):
    def __init__(self, parent, preferences, anki):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        bindings = [
            (self, 'accepted()', self.onAccept),
            (self.buttonContentColorFg, 'clicked()', self.onButtonColorFgClicked),
            (self.buttonContentColorBg, 'clicked()', self.onButtonColorBgClicked),
            (self.comboContentFontFamily, 'currentFontChanged(const QFont&)', self.onFontFamilyChanged),
            (self.spinContentFontSize, 'valueChanged(int)', self.onFontSizeChanged)
        ]

        for action, signal, callback in bindings:
            self.connect(action, QtCore.SIGNAL(signal), callback)

        self.preferences = preferences
        self.anki = anki

        self.dataToDialog()


    def dataToDialog(self):
        self.checkGeneralRecentLoad.setChecked(self.preferences.generalRecentLoad)
        self.checkGeneralReadingsStrip.setChecked(self.preferences.generalReadingsStrip)
        self.checkGeneralFindUpdates.setChecked(self.preferences.generalFindUpdates)

        self.updateSampleText()
        font = self.textContentSample.font()
        self.comboContentFontFamily.setCurrentFont(font)
        self.spinContentFontSize.setValue(font.pointSize())

        self.spinSearchScanMax.setValue(self.preferences.searchScanMax)
        self.spinSearchResultMax.setValue(self.preferences.searchResultMax)
        self.checkSearchGroupByExp.setChecked(self.preferences.searchGroupByExp)

        self.checkAnkiShowIcon.setChecked(self.preferences.ankiShowIcon)
        self.tabAnki.setEnabled(bool(self.anki))
        if self.anki:
            self.setAnkiFields(self.anki.fields(), self.preferences.ankiFields)


    def dialogToData(self):
        self.preferences.generalRecentLoad = self.checkGeneralRecentLoad.isChecked()
        self.preferences.generalReadingsStrip = self.checkGeneralReadingsStrip.isChecked()
        self.preferences.generalFindUpdates = self.checkGeneralFindUpdates.isChecked()

        self.preferences.searchScanMax = self.spinSearchScanMax.value()
        self.preferences.searchResultMax = self.spinSearchResultMax.value()
        self.preferences.searchGroupByExp = self.checkSearchGroupByExp.isChecked()

        self.preferences.ankiShowIcon = self.checkAnkiShowIcon.isChecked()
        if self.anki:
            self.preferences.ankiFields = self.ankiFields()


    def updateSampleText(self):
        palette = self.textContentSample.palette()
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(self.preferences.uiContentColorBg))
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor(self.preferences.uiContentColorFg))
        self.textContentSample.setPalette(palette)

        font = self.textContentSample.font()
        font.setFamily(self.preferences.uiContentFontFamily)
        font.setPointSize(self.preferences.uiContentFontSize)
        self.textContentSample.setFont(font)


    def setAnkiFields(self, fieldsAnki, fieldsPrefs):
        self.tableAnkiFields.setRowCount(len(fieldsAnki))

        for i, (name, required, unique) in enumerate(fieldsAnki):
            columns = list()

            itemName = QtGui.QTableWidgetItem(name)
            itemName.setFlags(QtCore.Qt.ItemIsSelectable)
            columns.append(itemName)

            itemValue = QtGui.QTableWidgetItem(fieldsPrefs.get(name, unicode()))
            columns.append(itemValue)

            itemRequired = QtGui.QTableWidgetItem()
            itemRequired.setFlags(QtCore.Qt.ItemIsUserCheckable)
            itemRequired.setCheckState(QtCore.Qt.Checked if required else QtCore.Qt.Unchecked)
            columns.append(itemRequired)

            itemUnique = QtGui.QTableWidgetItem()
            itemUnique.setFlags(QtCore.Qt.ItemIsUserCheckable)
            itemUnique.setCheckState(QtCore.Qt.Checked if unique else QtCore.Qt.Unchecked)
            columns.append(itemUnique)

            for j, column in enumerate(columns):
                self.tableAnkiFields.setItem(i, j, column)


    def ankiFields(self):
        result = dict()

        for i in range(0, self.tableAnkiFields.rowCount()):
            itemName = unicode(self.tableAnkiFields.item(i, 0).text())
            itemValue = unicode(self.tableAnkiFields.item(i, 1).text())
            result[itemName] = itemValue

        return result


    def onAccept(self):
        self.dialogToData()


    def onButtonColorFgClicked(self):
        color, ok = QtGui.QColorDialog.getRgba(self.preferences.uiContentColorFg, self)
        if ok:
            self.preferences.uiContentColorFg = color
            self.updateSampleText()


    def onButtonColorBgClicked(self):
        color, ok = QtGui.QColorDialog.getRgba(self.preferences.uiContentColorBg, self)
        if ok:
            self.preferences.uiContentColorBg = color
            self.updateSampleText()


    def onFontFamilyChanged(self, font):
        self.preferences.uiContentFontFamily = font.family()
        self.updateSampleText()


    def onFontSizeChanged(self, size):
        self.preferences.uiContentFontSize = size
        self.updateSampleText()
