# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.3.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMenuBar, QPlainTextEdit, QProgressBar, QPushButton,
    QSizePolicy, QSpinBox, QStatusBar, QTabWidget,
    QWidget)

class Ui_hashtagDropTarget(object):
    def setupUi(self, hashtagDropTarget):
        if not hashtagDropTarget.objectName():
            hashtagDropTarget.setObjectName(u"hashtagDropTarget")
        hashtagDropTarget.resize(1067, 560)
        self.centralwidget = QWidget(hashtagDropTarget)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_2 = QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_4 = QLabel(self.tab)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)

        self.browseButton = QPushButton(self.tab)
        self.browseButton.setObjectName(u"browseButton")

        self.gridLayout_2.addWidget(self.browseButton, 1, 1, 1, 1)

        self.iphone_mov = QSpinBox(self.tab)
        self.iphone_mov.setObjectName(u"iphone_mov")

        self.gridLayout_2.addWidget(self.iphone_mov, 4, 2, 1, 1)

        self.output = QPlainTextEdit(self.tab)
        self.output.setObjectName(u"output")

        self.gridLayout_2.addWidget(self.output, 16, 0, 1, 1)

        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 3, 1, 1, 1)

        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 4, 1, 1, 1)

        self.dji_pocket = QSpinBox(self.tab)
        self.dji_pocket.setObjectName(u"dji_pocket")

        self.gridLayout_2.addWidget(self.dji_pocket, 3, 2, 1, 1)

        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 5, 1, 1, 1)

        self.iphone_img = QSpinBox(self.tab)
        self.iphone_img.setObjectName(u"iphone_img")

        self.gridLayout_2.addWidget(self.iphone_img, 5, 2, 1, 1)

        self.path = QLineEdit(self.tab)
        self.path.setObjectName(u"path")

        self.gridLayout_2.addWidget(self.path, 1, 0, 1, 1)

        self.clearOutput = QPushButton(self.tab)
        self.clearOutput.setObjectName(u"clearOutput")

        self.gridLayout_2.addWidget(self.clearOutput, 16, 1, 1, 1)

        self.renameButton = QPushButton(self.tab)
        self.renameButton.setObjectName(u"renameButton")

        self.gridLayout_2.addWidget(self.renameButton, 3, 0, 1, 1)

        self.currentFilename = QLabel(self.tab)
        self.currentFilename.setObjectName(u"currentFilename")

        self.gridLayout_2.addWidget(self.currentFilename, 4, 0, 1, 1)

        self.fileProgress = QProgressBar(self.tab)
        self.fileProgress.setObjectName(u"fileProgress")
        self.fileProgress.setValue(0)
        self.fileProgress.setTextVisible(True)

        self.gridLayout_2.addWidget(self.fileProgress, 5, 0, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.sourceHashtags = QPlainTextEdit(self.tab_2)
        self.sourceHashtags.setObjectName(u"sourceHashtags")
        self.sourceHashtags.setGeometry(QRect(30, 40, 511, 151))
        self.hashtagOutput = QPlainTextEdit(self.tab_2)
        self.hashtagOutput.setObjectName(u"hashtagOutput")
        self.hashtagOutput.setGeometry(QRect(30, 200, 511, 111))
        self.shuffle = QPushButton(self.tab_2)
        self.shuffle.setObjectName(u"shuffle")
        self.shuffle.setGeometry(QRect(580, 150, 80, 26))
        self.hashtagTemplates = QListWidget(self.tab_2)
        self.hashtagTemplates.setObjectName(u"hashtagTemplates")
        self.hashtagTemplates.setGeometry(QRect(670, 250, 256, 192))
        self.hashtagTemplates.setSelectionMode(QAbstractItemView.MultiSelection)
        self.pasteFromClipboard = QPushButton(self.tab_2)
        self.pasteFromClipboard.setObjectName(u"pasteFromClipboard")
        self.pasteFromClipboard.setGeometry(QRect(670, 200, 121, 31))
        self.pasteHashtagTrends = QPushButton(self.tab_2)
        self.pasteHashtagTrends.setObjectName(u"pasteHashtagTrends")
        self.pasteHashtagTrends.setGeometry(QRect(800, 200, 101, 34))
        self.hashtagManagerButton = QPushButton(self.tab_2)
        self.hashtagManagerButton.setObjectName(u"hashtagManagerButton")
        self.hashtagManagerButton.setGeometry(QRect(890, 120, 131, 34))
        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout.addWidget(self.tabWidget, 2, 1, 1, 1)

        hashtagDropTarget.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(hashtagDropTarget)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1067, 30))
        hashtagDropTarget.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(hashtagDropTarget)
        self.statusbar.setObjectName(u"statusbar")
        hashtagDropTarget.setStatusBar(self.statusbar)

        self.retranslateUi(hashtagDropTarget)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(hashtagDropTarget)
    # setupUi

    def retranslateUi(self, hashtagDropTarget):
        hashtagDropTarget.setWindowTitle(QCoreApplication.translate("hashtagDropTarget", u"MainWindow", None))
        self.label_4.setText(QCoreApplication.translate("hashtagDropTarget", u"Path:", None))
        self.browseButton.setText(QCoreApplication.translate("hashtagDropTarget", u"Browse...", None))
        self.label.setText(QCoreApplication.translate("hashtagDropTarget", u"DHI Pocket:", None))
        self.label_2.setText(QCoreApplication.translate("hashtagDropTarget", u"iPhone MOV", None))
        self.label_3.setText(QCoreApplication.translate("hashtagDropTarget", u"JPEG", None))
        self.clearOutput.setText(QCoreApplication.translate("hashtagDropTarget", u"Clear", None))
        self.renameButton.setText(QCoreApplication.translate("hashtagDropTarget", u"Rename", None))
        self.currentFilename.setText(QCoreApplication.translate("hashtagDropTarget", u"None", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("hashtagDropTarget", u"File Raname", None))
        self.shuffle.setText(QCoreApplication.translate("hashtagDropTarget", u"Shuffle", None))
        self.pasteFromClipboard.setText(QCoreApplication.translate("hashtagDropTarget", u"Paste Hashtags", None))
        self.pasteHashtagTrends.setText(QCoreApplication.translate("hashtagDropTarget", u"Paste Trends", None))
        self.hashtagManagerButton.setText(QCoreApplication.translate("hashtagDropTarget", u"Hashtag Manager", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("hashtagDropTarget", u"Hashtags", None))
    # retranslateUi

