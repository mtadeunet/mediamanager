# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'hashtagManagerDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QHeaderView, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QWidget)

class Ui_hashtagManager(object):
    def setupUi(self, hashtagManager):
        if not hashtagManager.objectName():
            hashtagManager.setObjectName(u"hashtagManager")
        hashtagManager.resize(993, 575)
        hashtagManager.setMinimumSize(QSize(200, 200))
        self.gridLayout = QGridLayout(hashtagManager)
        self.gridLayout.setObjectName(u"gridLayout")
        self.collectionWidget = QListWidget(hashtagManager)
        self.collectionWidget.setObjectName(u"collectionWidget")

        self.gridLayout.addWidget(self.collectionWidget, 0, 0, 2, 2)

        self.searchEdit = QLineEdit(hashtagManager)
        self.searchEdit.setObjectName(u"searchEdit")

        self.gridLayout.addWidget(self.searchEdit, 0, 2, 1, 1)

        self.hashtagTableWidget = QTableWidget(hashtagManager)
        if (self.hashtagTableWidget.columnCount() < 6):
            self.hashtagTableWidget.setColumnCount(6)
        self.hashtagTableWidget.setObjectName(u"hashtagTableWidget")
        self.hashtagTableWidget.setRowCount(0)
        self.hashtagTableWidget.setColumnCount(6)

        self.gridLayout.addWidget(self.hashtagTableWidget, 1, 2, 1, 1)

        self.addCollectionButton = QPushButton(hashtagManager)
        self.addCollectionButton.setObjectName(u"addCollectionButton")

        self.gridLayout.addWidget(self.addCollectionButton, 2, 0, 1, 1)

        self.removeCollectionButton = QPushButton(hashtagManager)
        self.removeCollectionButton.setObjectName(u"removeCollectionButton")

        self.gridLayout.addWidget(self.removeCollectionButton, 2, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(hashtagManager)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 2, 2, 1, 1)


        self.retranslateUi(hashtagManager)
        self.buttonBox.accepted.connect(hashtagManager.accept)
        self.buttonBox.rejected.connect(hashtagManager.reject)

        QMetaObject.connectSlotsByName(hashtagManager)
    # setupUi

    def retranslateUi(self, hashtagManager):
        hashtagManager.setWindowTitle(QCoreApplication.translate("hashtagManager", u"Dialog", None))
        self.addCollectionButton.setText(QCoreApplication.translate("hashtagManager", u"+", None))
        self.removeCollectionButton.setText(QCoreApplication.translate("hashtagManager", u"-", None))
    # retranslateUi

