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
from gen import preferences_ui
import copy


class DialogPreferences(QtGui.QDialog, preferences_ui.Ui_DialogPreferences):
    def __init__(self, parent, preferences, anki):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.accepted.connect(self.onAccept)
        self.buttonColorBg.clicked.connect(self.onButtonColorBgClicked)
        self.buttonColorFg.clicked.connect(self.onButtonColorFgClicked)
        self.comboBoxModel.currentIndexChanged.connect(self.onModelChanged)
        self.comboFontFamily.currentFontChanged.connect(self.onFontFamilyChanged)
        self.spinFontSize.valueChanged.connect(self.onFontSizeChanged)

        self.preferences = preferences
        self.anki = anki

        self.dataToDialog()


    def dataToDialog(self):
        self.checkCheckForUpdates.setChecked(self.preferences['checkForUpdates'])
        self.checkLoadRecentFile.setChecked(self.preferences['loadRecentFile'])
        self.checkStripReadings.setChecked(self.preferences['stripReadings'])
        self.spinScanLength.setValue(self.preferences['scanLength'])

        self.updateSampleText()
        font = self.textSample.font()
        self.comboFontFamily.setCurrentFont(font)
        self.spinFontSize.setValue(font.pointSize())

        if self.anki is not None:
            self.tabAnki.setEnabled(True)
            self.profiles = copy.deepcopy(self.preferences['profiles'])
            self.profileToDialog()


    def dialogToData(self):
        self.preferences['checkForUpdates'] = self.checkCheckForUpdates.isChecked()
        self.preferences['loadRecentFile'] = self.checkLoadRecentFile.isChecked()
        self.preferences['scanLength'] = self.spinScanLength.value()
        self.preferences['stripReadings'] = self.checkStripReadings.isChecked()

        if self.anki is not None:
            self.dialogToProfile()
            self.preferences['profiles'] = self.profiles


    def dialogToProfile(self):
        self.setActiveProfile({
            'deck': unicode(self.comboBoxDeck.currentText()),
            'model': unicode(self.comboBoxModel.currentText()),
            'fields': self.ankiFields()
        })


    def profileToDialog(self):
        profile = self.activeProfile()

        deck = str() if profile is None else profile['deck']
        model = str() if profile is None else profile['model']

        self.comboBoxDeck.addItems(self.anki.deckNames())
        self.comboBoxDeck.setCurrentIndex(self.comboBoxDeck.findText(deck))
        self.comboBoxModel.blockSignals(True)
        self.comboBoxModel.addItems(self.anki.modelNames())
        self.comboBoxModel.blockSignals(False)
        self.comboBoxModel.setCurrentIndex(self.comboBoxModel.findText(model))


    def updateSampleText(self):
        palette = self.textSample.palette()
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(self.preferences['bgColor']))
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor(self.preferences['fgColor']))
        self.textSample.setPalette(palette)

        font = self.textSample.font()
        font.setFamily(self.preferences['fontFamily'])
        font.setPointSize(self.preferences['fontSize'])
        self.textSample.setFont(font)


    def setAnkiFields(self, fields, fieldsPrefs):
        if fields is None:
            fields = list()

        self.tableFields.setRowCount(len(fields))

        for i, name in enumerate(fields):
            columns = list()

            itemName = QtGui.QTableWidgetItem(name)
            itemName.setFlags(QtCore.Qt.ItemIsSelectable)
            columns.append(itemName)

            itemValue = QtGui.QTableWidgetItem(fieldsPrefs.get(name, unicode()))
            columns.append(itemValue)

            for j, column in enumerate(columns):
                self.tableFields.setItem(i, j, column)


    def ankiFields(self):
        result = dict()

        for i in range(0, self.tableFields.rowCount()):
            itemName = unicode(self.tableFields.item(i, 0).text())
            itemValue = unicode(self.tableFields.item(i, 1).text())
            result[itemName] = itemValue

        return result


    def onAccept(self):
        self.dialogToData()


    def onButtonColorFgClicked(self):
        color, ok = QtGui.QColorDialog.getRgba(self.preferences['fgColor'], self)
        if ok:
            self.preferences['fgColor'] = color
            self.updateSampleText()


    def onButtonColorBgClicked(self):
        color, ok = QtGui.QColorDialog.getRgba(self.preferences['bgColor'], self)
        if ok:
            self.preferences['bgColor'] = color
            self.updateSampleText()


    def onFontFamilyChanged(self, font):
        self.preferences['fontFamily'] = str(font.family())
        self.updateSampleText()


    def onFontSizeChanged(self, size):
        self.preferences['fontSize'] = size
        self.updateSampleText()


    def onModelChanged(self, index):
        modelName = self.comboBoxModel.currentText()
        fieldNames = self.anki.modelFieldNames(modelName) or list()

        profile = self.activeProfile()
        fields = dict() if profile is None else profile['fields']

        self.setAnkiFields(fieldNames, fields)


    def activeProfile(self):
        key = 'vocab' if self.radioButtonVocab.isChecked() else 'kanji'
        return self.profiles.get(key)


    def setActiveProfile(self, profile):
        key = 'vocab' if self.radioButtonVocab.isChecked() else 'kanji'
        self.profiles[key] = profile
