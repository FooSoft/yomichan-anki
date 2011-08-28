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
            (self, 'accepted()', self.__onAccept),
            (self.buttonContentColorFg, 'clicked()', self.__onButtonColorFgClicked),
            (self.buttonContentColorBg, 'clicked()', self.__onButtonColorBgClicked),
            (self.comboContentFontFamily, 'currentFontChanged(const QFont&)', self.__onFontFamilyChanged),
            (self.spinContentFontSize, 'valueChanged(int)', self.__onFontSizeChanged)
        ]

        for action, signal, callback in bindings:
            self.connect(action, QtCore.SIGNAL(signal), callback)

        self.__preferences = preferences
        self.__anki = anki

        self.__dataToDialog()


    def __dataToDialog(self):
        self.checkGeneralRecentLoad.setChecked(self.__preferences.generalRecentLoad)
        self.checkGeneralReadingsStrip.setChecked(self.__preferences.generalReadingsStrip)
        self.checkGeneralFindUpdates.setChecked(self.__preferences.generalFindUpdates)

        self.__updateSampleText()
        font = self.textContentSample.font()
        self.comboContentFontFamily.setCurrentFont(font)
        self.spinContentFontSize.setValue(font.pointSize())

        self.spinSearchScanMax.setValue(self.__preferences.searchScanMax)
        self.spinSearchResultMax.setValue(self.__preferences.searchResultMax)
        self.checkSearchGroupByExp.setChecked(self.__preferences.searchGroupByExp)

        self.checkAnkiShowIcon.setChecked(self.__preferences.ankiShowIcon)
        self.tabAnki.setEnabled(bool(self.__anki))
        if self.__anki:
            self.__setAnkiFields(self.__anki.fields(), self.__preferences.ankiFields)


    def __dialogToData(self):
        self.__preferences.generalRecentLoad = self.checkGeneralRecentLoad.isChecked()
        self.__preferences.generalReadingsStrip = self.checkGeneralReadingsStrip.isChecked()
        self.__preferences.generalFindUpdates = self.checkGeneralFindUpdates.isChecked()

        self.__preferences.searchScanMax = self.spinSearchScanMax.value()
        self.__preferences.searchResultMax = self.spinSearchResultMax.value()
        self.__preferences.searchGroupByExp = self.checkSearchGroupByExp.isChecked()

        self.__preferences.ankiShowIcon = self.checkAnkiShowIcon.isChecked()
        if self.__anki:
            self.__preferences.ankiFields = self.__ankiFields()


    def __updateSampleText(self):
        palette = self.textContentSample.palette()
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(self.__preferences.uiContentColorBg))
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor(self.__preferences.uiContentColorFg))
        self.textContentSample.setPalette(palette)

        font = self.textContentSample.font()
        font.setFamily(self.__preferences.uiContentFontFamily)
        font.setPointSize(self.__preferences.uiContentFontSize)
        self.textContentSample.setFont(font)


    def __setAnkiFields(self, fieldsAnki, fieldsPrefs):
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


    def __ankiFields(self):
        result = dict()

        for i in range(0, self.tableAnkiFields.rowCount()):
            itemName = unicode(self.tableAnkiFields.item(i, 0).text())
            itemValue = unicode(self.tableAnkiFields.item(i, 1).text())
            result[itemName] = itemValue

        return result


    def __onAccept(self):
        self.__dialogToData()


    def __onButtonColorFgClicked(self):
        color, ok = QtGui.QColorDialog.getRgba(self.__preferences.uiContentColorFg, self)
        if ok:
            self.__preferences.uiContentColorFg = color
            self.__updateSampleText()


    def __onButtonColorBgClicked(self):
        color, ok = QtGui.QColorDialog.getRgba(self.__preferences.uiContentColorBg, self)
        if ok:
            self.__preferences.uiContentColorBg = color
            self.__updateSampleText()


    def __onFontFamilyChanged(self, font):
        self.__preferences.uiContentFontFamily = font.family()
        self.__updateSampleText()


    def __onFontSizeChanged(self, size):
        self.__preferences.uiContentFontSize = size
        self.__updateSampleText()
