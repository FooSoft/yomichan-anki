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
from util import buildResPath
from ui_gen import preferences


class DialogPreferences(QtGui.QDialog, preferences.Ui_DialogPreferences):
    def __init__(self, parent, preferences, anki):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.accepted.connect(self.onAccept)
        self.buttonContentColorFg.clicked.connect(self.onButtonColorFgClicked)
        self.buttonContentColorBg.clicked.connect(self.onButtonColorBgClicked)
        self.comboContentFontFamily.currentFontChanged.connect(self.onFontFamilyChanged)
        self.spinContentFontSize.valueChanged.connect(self.onFontSizeChanged)
        self.comboBoxAnkiModel.currentIndexChanged.connect(self.onAnkiModelChanged)

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

        self.tabAnki.setEnabled(self.anki is not None)
        if self.anki:
            self.comboBoxAnkiDeck.addItems(self.anki.deckNames())
            self.comboBoxAnkiDeck.setCurrentIndex(self.comboBoxAnkiDeck.findText(self.preferences.ankiDeck))
            self.comboBoxAnkiModel.blockSignals(True)
            self.comboBoxAnkiModel.addItems(self.anki.modelNames())
            self.comboBoxAnkiModel.blockSignals(False)
            self.comboBoxAnkiModel.setCurrentIndex(self.comboBoxAnkiModel.findText(self.preferences.ankiModel))


    def dialogToData(self):
        self.preferences.generalRecentLoad = self.checkGeneralRecentLoad.isChecked()
        self.preferences.generalReadingsStrip = self.checkGeneralReadingsStrip.isChecked()
        self.preferences.generalFindUpdates = self.checkGeneralFindUpdates.isChecked()

        self.preferences.searchScanMax = self.spinSearchScanMax.value()
        self.preferences.searchResultMax = self.spinSearchResultMax.value()
        self.preferences.searchGroupByExp = self.checkSearchGroupByExp.isChecked()

        if self.anki:
            self.preferences.ankiDeck = unicode(self.comboBoxAnkiDeck.currentText())
            self.preferences.ankiModel = unicode(self.comboBoxAnkiModel.currentText())
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
        if fieldsAnki is None:
            fieldsAnki = list()

        self.tableAnkiFields.setRowCount(len(fieldsAnki))

        for i, name in enumerate(fieldsAnki):
            columns = list()

            itemName = QtGui.QTableWidgetItem(name)
            itemName.setFlags(QtCore.Qt.ItemIsSelectable)
            columns.append(itemName)

            itemValue = QtGui.QTableWidgetItem(fieldsPrefs.get(name, unicode()))
            columns.append(itemValue)

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


    def onAnkiModelChanged(self, index):
        modelName = self.comboBoxAnkiModel.currentText()
        fieldNames = self.anki.modelFieldNames(modelName) or list()
        self.setAnkiFields(fieldNames, self.preferences.ankiFields)
