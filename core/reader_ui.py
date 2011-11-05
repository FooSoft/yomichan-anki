# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dev/reader.ui'
#
# Created: Fri Oct  7 08:55:15 2011
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindowReader(object):
    def setupUi(self, MainWindowReader):
        MainWindowReader.setObjectName(_fromUtf8("MainWindowReader"))
        MainWindowReader.resize(900, 650)
        MainWindowReader.setAcceptDrops(True)
        MainWindowReader.setWindowTitle(QtGui.QApplication.translate("MainWindowReader", "Yomichan", None, QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/logos/logos/logo32x32.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindowReader.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindowReader)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.textContent = QtGui.QPlainTextEdit(self.centralwidget)
        self.textContent.setMouseTracking(True)
        self.textContent.setReadOnly(True)
        self.textContent.setObjectName(_fromUtf8("textContent"))
        self.horizontalLayout.addWidget(self.textContent)
        MainWindowReader.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindowReader)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindowReader", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuOpenArchive = QtGui.QMenu(self.menuFile)
        self.menuOpenArchive.setTitle(QtGui.QApplication.translate("MainWindowReader", "Open from &archive", None, QtGui.QApplication.UnicodeUTF8))
        self.menuOpenArchive.setObjectName(_fromUtf8("menuOpenArchive"))
        self.menuOpenArchive.setEnabled(False)
        self.menuOpenRecent = QtGui.QMenu(self.menuFile)
        self.menuOpenRecent.setTitle(QtGui.QApplication.translate("MainWindowReader", "Open &recent", None, QtGui.QApplication.UnicodeUTF8))
        self.menuOpenRecent.setObjectName(_fromUtf8("menuOpenRecent"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setTitle(QtGui.QApplication.translate("MainWindowReader", "&Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindowReader", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setTitle(QtGui.QApplication.translate("MainWindowReader", "&View", None, QtGui.QApplication.UnicodeUTF8))
        self.menuView.setObjectName(_fromUtf8("menuView"))
        self.menuTextSize = QtGui.QMenu(self.menuView)
        self.menuTextSize.setTitle(QtGui.QApplication.translate("MainWindowReader", "&Zoom", None, QtGui.QApplication.UnicodeUTF8))
        self.menuTextSize.setObjectName(_fromUtf8("menuTextSize"))
        MainWindowReader.setMenuBar(self.menubar)
        self.toolBar = QtGui.QToolBar(MainWindowReader)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindowReader", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setIconSize(QtCore.QSize(16, 16))
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindowReader.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.dockDefinitions = QtGui.QDockWidget(MainWindowReader)
        self.dockDefinitions.setWindowTitle(QtGui.QApplication.translate("MainWindowReader", "Definitions", None, QtGui.QApplication.UnicodeUTF8))
        self.dockDefinitions.setObjectName(_fromUtf8("dockDefinitions"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.textDefinitions = QtGui.QTextBrowser(self.dockWidgetContents)
        self.textDefinitions.setAcceptDrops(False)
        self.textDefinitions.setOpenLinks(False)
        self.textDefinitions.setObjectName(_fromUtf8("textDefinitions"))
        self.verticalLayout.addWidget(self.textDefinitions)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setText(QtGui.QApplication.translate("MainWindowReader", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.textDefinitionSearch = QtGui.QLineEdit(self.dockWidgetContents)
        self.textDefinitionSearch.setObjectName(_fromUtf8("textDefinitionSearch"))
        self.horizontalLayout_3.addWidget(self.textDefinitionSearch)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.dockDefinitions.setWidget(self.dockWidgetContents)
        MainWindowReader.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockDefinitions)
        self.statusBar = QtGui.QStatusBar(MainWindowReader)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindowReader.setStatusBar(self.statusBar)
        self.dockAnki = QtGui.QDockWidget(MainWindowReader)
        self.dockAnki.setWindowTitle(QtGui.QApplication.translate("MainWindowReader", "Anki", None, QtGui.QApplication.UnicodeUTF8))
        self.dockAnki.setObjectName(_fromUtf8("dockAnki"))
        self.dockWidgetContents_2 = QtGui.QWidget()
        self.dockWidgetContents_2.setObjectName(_fromUtf8("dockWidgetContents_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.listDefinitions = QtGui.QListWidget(self.dockWidgetContents_2)
        self.listDefinitions.setObjectName(_fromUtf8("listDefinitions"))
        self.verticalLayout_2.addWidget(self.listDefinitions)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_3 = QtGui.QLabel(self.dockWidgetContents_2)
        self.label_3.setText(QtGui.QApplication.translate("MainWindowReader", "Active tag(s)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        self.comboTags = QtGui.QComboBox(self.dockWidgetContents_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboTags.sizePolicy().hasHeightForWidth())
        self.comboTags.setSizePolicy(sizePolicy)
        self.comboTags.setEditable(True)
        self.comboTags.setObjectName(_fromUtf8("comboTags"))
        self.horizontalLayout_2.addWidget(self.comboTags)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.dockAnki.setWidget(self.dockWidgetContents_2)
        MainWindowReader.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockAnki)
        self.actionOpen = QtGui.QAction(MainWindowReader)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/folder_page.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon1)
        self.actionOpen.setText(QtGui.QApplication.translate("MainWindowReader", "&Open...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setToolTip(QtGui.QApplication.translate("MainWindowReader", "Open file", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setShortcut(QtGui.QApplication.translate("MainWindowReader", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setIconVisibleInMenu(True)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionQuit = QtGui.QAction(MainWindowReader)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/cross.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionQuit.setIcon(icon2)
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindowReader", "&Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setToolTip(QtGui.QApplication.translate("MainWindowReader", "Quit Yomichan", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setShortcut(QtGui.QApplication.translate("MainWindowReader", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setIconVisibleInMenu(True)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionPreferences = QtGui.QAction(MainWindowReader)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/wrench.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPreferences.setIcon(icon3)
        self.actionPreferences.setText(QtGui.QApplication.translate("MainWindowReader", "&Preferences...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setToolTip(QtGui.QApplication.translate("MainWindowReader", "Edit preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setIconVisibleInMenu(True)
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))
        self.actionAbout = QtGui.QAction(MainWindowReader)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/information.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout.setIcon(icon4)
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindowReader", "&About...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setToolTip(QtGui.QApplication.translate("MainWindowReader", "About Yomichan", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setShortcut(QtGui.QApplication.translate("MainWindowReader", "F1", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setIconVisibleInMenu(True)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionZoomIn = QtGui.QAction(MainWindowReader)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/magnifier_zoom_in.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomIn.setIcon(icon5)
        self.actionZoomIn.setText(QtGui.QApplication.translate("MainWindowReader", "Zoom &in", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomIn.setShortcut(QtGui.QApplication.translate("MainWindowReader", "Ctrl++", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomIn.setIconVisibleInMenu(True)
        self.actionZoomIn.setObjectName(_fromUtf8("actionZoomIn"))
        self.actionZoomOut = QtGui.QAction(MainWindowReader)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/magifier_zoom_out.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomOut.setIcon(icon6)
        self.actionZoomOut.setText(QtGui.QApplication.translate("MainWindowReader", "Zoom &out", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomOut.setShortcut(QtGui.QApplication.translate("MainWindowReader", "Ctrl+-", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomOut.setIconVisibleInMenu(True)
        self.actionZoomOut.setObjectName(_fromUtf8("actionZoomOut"))
        self.actionZoomReset = QtGui.QAction(MainWindowReader)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/magnifier.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomReset.setIcon(icon7)
        self.actionZoomReset.setText(QtGui.QApplication.translate("MainWindowReader", "&Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomReset.setToolTip(QtGui.QApplication.translate("MainWindowReader", "Reset zoom", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomReset.setShortcut(QtGui.QApplication.translate("MainWindowReader", "Ctrl+0", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomReset.setIconVisibleInMenu(True)
        self.actionZoomReset.setObjectName(_fromUtf8("actionZoomReset"))
        self.actionFind = QtGui.QAction(MainWindowReader)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/find.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFind.setIcon(icon8)
        self.actionFind.setText(QtGui.QApplication.translate("MainWindowReader", "&Find...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFind.setToolTip(QtGui.QApplication.translate("MainWindowReader", "Find text", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFind.setShortcut(QtGui.QApplication.translate("MainWindowReader", "Ctrl+F", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFind.setIconVisibleInMenu(True)
        self.actionFind.setObjectName(_fromUtf8("actionFind"))
        self.actionFindNext = QtGui.QAction(MainWindowReader)
        self.actionFindNext.setText(QtGui.QApplication.translate("MainWindowReader", "Find &next", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFindNext.setToolTip(QtGui.QApplication.translate("MainWindowReader", "Find text again", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFindNext.setShortcut(QtGui.QApplication.translate("MainWindowReader", "F3", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFindNext.setObjectName(_fromUtf8("actionFindNext"))
        self.actionToggleWrap = QtGui.QAction(MainWindowReader)
        self.actionToggleWrap.setCheckable(True)
        self.actionToggleWrap.setChecked(True)
        self.actionToggleWrap.setText(QtGui.QApplication.translate("MainWindowReader", "&Word wrap", None, QtGui.QApplication.UnicodeUTF8))
        self.actionToggleWrap.setToolTip(QtGui.QApplication.translate("MainWindowReader", "Toggle word wrap", None, QtGui.QApplication.UnicodeUTF8))
        self.actionToggleWrap.setObjectName(_fromUtf8("actionToggleWrap"))
        self.actionToggleDefinitions = QtGui.QAction(MainWindowReader)
        self.actionToggleDefinitions.setCheckable(True)
        self.actionToggleDefinitions.setText(QtGui.QApplication.translate("MainWindowReader", "&Definitions", None, QtGui.QApplication.UnicodeUTF8))
        self.actionToggleDefinitions.setToolTip(QtGui.QApplication.translate("MainWindowReader", "Toggle definitions", None, QtGui.QApplication.UnicodeUTF8))
        self.actionToggleDefinitions.setObjectName(_fromUtf8("actionToggleDefinitions"))
        self.actionCopyDefinition = QtGui.QAction(MainWindowReader)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/page_copy.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCopyDefinition.setIcon(icon9)
        self.actionCopyDefinition.setText(QtGui.QApplication.translate("MainWindowReader", "Copy &definition", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopyDefinition.setShortcut(QtGui.QApplication.translate("MainWindowReader", "Ctrl+D", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopyDefinition.setIconVisibleInMenu(True)
        self.actionCopyDefinition.setObjectName(_fromUtf8("actionCopyDefinition"))
        self.actionCopyAllDefinitions = QtGui.QAction(MainWindowReader)
        self.actionCopyAllDefinitions.setText(QtGui.QApplication.translate("MainWindowReader", "Copy &all definitions", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopyAllDefinitions.setObjectName(_fromUtf8("actionCopyAllDefinitions"))
        self.actionHomepage = QtGui.QAction(MainWindowReader)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/world_go.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionHomepage.setIcon(icon10)
        self.actionHomepage.setText(QtGui.QApplication.translate("MainWindowReader", "&Homepage...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionHomepage.setToolTip(QtGui.QApplication.translate("MainWindowReader", "Yomichan homepage", None, QtGui.QApplication.UnicodeUTF8))
        self.actionHomepage.setIconVisibleInMenu(True)
        self.actionHomepage.setObjectName(_fromUtf8("actionHomepage"))
        self.actionToggleAnki = QtGui.QAction(MainWindowReader)
        self.actionToggleAnki.setCheckable(True)
        self.actionToggleAnki.setText(QtGui.QApplication.translate("MainWindowReader", "&Anki", None, QtGui.QApplication.UnicodeUTF8))
        self.actionToggleAnki.setObjectName(_fromUtf8("actionToggleAnki"))
        self.actionCopySentence = QtGui.QAction(MainWindowReader)
        self.actionCopySentence.setText(QtGui.QApplication.translate("MainWindowReader", "Copy sen&tence", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopySentence.setShortcut(QtGui.QApplication.translate("MainWindowReader", "Ctrl+T", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopySentence.setObjectName(_fromUtf8("actionCopySentence"))
        self.actionFeedback = QtGui.QAction(MainWindowReader)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/icons/email.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFeedback.setIcon(icon11)
        self.actionFeedback.setText(QtGui.QApplication.translate("MainWindowReader", "&Feedback...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFeedback.setObjectName(_fromUtf8("actionFeedback"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.menuOpenArchive.menuAction())
        self.menuFile.addAction(self.menuOpenRecent.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuEdit.addAction(self.actionCopyDefinition)
        self.menuEdit.addAction(self.actionCopyAllDefinitions)
        self.menuEdit.addAction(self.actionCopySentence)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionFind)
        self.menuEdit.addAction(self.actionFindNext)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionPreferences)
        self.menuHelp.addAction(self.actionHomepage)
        self.menuHelp.addAction(self.actionFeedback)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        self.menuTextSize.addAction(self.actionZoomIn)
        self.menuTextSize.addAction(self.actionZoomOut)
        self.menuTextSize.addSeparator()
        self.menuTextSize.addAction(self.actionZoomReset)
        self.menuView.addAction(self.menuTextSize.menuAction())
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionToggleDefinitions)
        self.menuView.addAction(self.actionToggleAnki)
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionToggleWrap)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionZoomIn)
        self.toolBar.addAction(self.actionZoomOut)
        self.toolBar.addAction(self.actionZoomReset)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionFind)

        self.retranslateUi(MainWindowReader)
        QtCore.QObject.connect(self.actionToggleDefinitions, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.dockDefinitions.setVisible)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindowReader.close)
        QtCore.QObject.connect(self.actionToggleAnki, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.dockAnki.setVisible)
        QtCore.QMetaObject.connectSlotsByName(MainWindowReader)

    def retranslateUi(self, MainWindowReader):
        pass

import resources_rc
