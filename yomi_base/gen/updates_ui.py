# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/updates.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DialogUpdates(object):
    def setupUi(self, DialogUpdates):
        DialogUpdates.setObjectName(_fromUtf8("DialogUpdates"))
        DialogUpdates.resize(500, 400)
        self.verticalLayout = QtGui.QVBoxLayout(DialogUpdates)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.labelUpdates = QtGui.QLabel(DialogUpdates)
        self.labelUpdates.setWordWrap(True)
        self.labelUpdates.setOpenExternalLinks(True)
        self.labelUpdates.setObjectName(_fromUtf8("labelUpdates"))
        self.verticalLayout.addWidget(self.labelUpdates)
        self.textBrowser = QtGui.QTextBrowser(DialogUpdates)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.verticalLayout.addWidget(self.textBrowser)
        self.buttonBox = QtGui.QDialogButtonBox(DialogUpdates)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DialogUpdates)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DialogUpdates.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DialogUpdates.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogUpdates)

    def retranslateUi(self, DialogUpdates):
        DialogUpdates.setWindowTitle(_translate("DialogUpdates", "Update Checker", None))
        self.labelUpdates.setText(_translate("DialogUpdates", "<p>A new version of Yomichan is available for download!</p>\n"
"\n"
"<p>You can download this update (version {0} to version {1}) from the add-ons section on <a href=\"https://ankiweb.net/shared/info/934748696\">Anki Online</a> or directly from the <a href=\"https://foosoft.net/projects/yomichan\">Yomichan homepage</a>.</p>\n"
"\n"
"<p>Changes from your version are listed below:</p>", None))

