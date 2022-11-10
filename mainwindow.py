# This Python file uses the following encoding: utf-8
# flake8: noqa

import os
from pathlib import Path
import sys
import random
import json
import threading

from datetime import datetime, timedelta
# from tkinter.ttk import Treeview
from exiftool import ExifToolHelper

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QListWidgetItem,
    QListWidget,
    QProgressBar,
    QPushButton,
    QTreeWidgetItem,
)
from PySide6.QtGui import QDropEvent
from PySide6.QtCore import QFile, Slot, Qt, QByteArray, QObject
from PySide6.QtUiTools import QUiLoader
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from database import HashtagTable, CollectionsTable, Table, DatabaseExecution, UsersTable, UserTable
from Inssist import InssistThread
import time
import common

EXIFTOOL_FIELDS = ["QuickTime:CreationDate", "QuickTime:CreateDate",
                   "Composite:SubSecDateTimeOriginal", "EXIF:DateTimeOriginal"]


class MainWindow(QMainWindow):

    class TreeWidget(QObject):
        def __init__(self, parent, treeWidget) -> None:
            super().__init__(parent)
            self._treeWidget = treeWidget

            self._unknown = self.tree.topLevelItem(0)
            self._invalid = self.tree.topLevelItem(1)
            self._low = self.tree.topLevelItem(2)
            self._medium = self.tree.topLevelItem(3)
            self._high = self.tree.topLevelItem(4)
            self._vhigh = self.tree.topLevelItem(5)

        def _getListFromItem(self, item: QTreeWidgetItem):
            result = []
            for index in range(item.childCount()):
                child = item.child(index)
                result.append((child.text(0), float(child.text(1))))
            return result

        @property
        def invalidHashtags(self):
            return self._getListFromItem(self._invalid)

        @property
        def unknownHashtags(self):
            return self._getListFromItem(self._unknown)

        @property
        def lowHashtags(self):
            return self._getListFromItem(self._low)

        @property
        def mediumHashtags(self):
            return self._getListFromItem(self._medium)

        @property
        def highHashtags(self):
            return self._getListFromItem(self._high)

        @property
        def vhighHashtags(self):
            return self._getListFromItem(self._vhigh)

        @property
        def tree(self):
            return self._treeWidget

        def clearTopLevelItems(self):
            for topLevelItem in [self._unknown, self._invalid, self._low, self._medium, self._high, self._vhigh]:
                for item in reversed(range(topLevelItem.childCount())):
                    topLevelItem.removeChild(topLevelItem.child(item))

        def getCleanTopLevelItem(self, index):
            item = self.ui.hashtagsFromCollections.topLevelItem(index)
            for i in reversed(range(item.childCount())):
                item.removeChild(item.child(i))
            return item


        def _createItem(self, record, score, color):
            item = QTreeWidgetItem()
            item.setData(0, Qt.DisplayRole, record["name"])
            item.setData(1, Qt.DisplayRole, score)
            item.setBackground(0, color)
            item.setBackground(1, color)
            return item

        def addChildToTopLevelItem(self, topLevelItem, record, score):
            found = self.ui.hashtagsFromCollections.findItems(record["name"], Qt.MatchContains|Qt.MatchRecursive, 0)
            if not found:
                item = QTreeWidgetItem()
                item.setData(0, Qt.DisplayRole, record["name"])
                item.setData(1, Qt.DisplayRole, score)
                topLevelItem.addChild(item)

        def addItem(self, record):
            if record["last_update"] == 0:
                item = self._unknown
                score = '-'
            elif record["last_update"] == 9999999999:
                score = '-'
                item = self._invalid
            else:
                score = common.defineScore(record, UserTable(self.parent().ui.users.currentText()))


                if score < 1:
                    item = self._low
                elif score < 2:
                    item = self._medium
                elif score < 3:
                    item = self._high
                else:
                    item = self._vhigh

            color = common.defineRowColor(record, score)

            found = self.tree.findItems(record["name"], Qt.MatchContains|Qt.MatchRecursive, 0)
            if not found:
                item.addChild(self._createItem(record, score, color))


    def __init__(self):
        super(MainWindow, self).__init__()
        self.exif = ExifToolHelper()
        self._collectionsTable = CollectionsTable()
        self._hashtags_table = HashtagTable()
        self._inssist = InssistThread.get()
        self._user_table = UsersTable()

        self.load_ui()

        self._hashtagDistribution = MainWindow.TreeWidget(self, self.ui.hashtagDistribution)


    def load_ui(self):
        loader = QUiLoader()
        # path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile("form.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)  # self.ui same as self.centralWidget()
        ui_file.close()

        self.ui.renameButton.clicked.connect(self.renameButtonClicked)
        self.ui.clearOutput.clicked.connect(self.ui.output.clear)
        self.ui.browseButton.clicked.connect(self.browse)
        self.ui.shuffle.clicked.connect(self.shuffleHashtags)

        self.ui.hashtagManagerButton.clicked.connect(self.hashtagManager)

        items = [item["name"] for item in self._collectionsTable.select(order=['name']).items]
        self.ui.hashtagCollections.addItems(items)

        self.ui.clearSelection.clicked.connect(self.ui.hashtagCollections.clearSelection)
        self.ui.hashtagCollections.itemSelectionChanged.connect(self.collectionSelectionChanged)
        self.ui.generateHashtags.clicked.connect(self.generateHashtags)

        for user in self._user_table.select().items:
            self.ui.users.addItem(user["name"])

    @Slot()
    def generateHashtags(self):
        result = []
        # get from low
        invalid = self._hashtagDistribution.invalidHashtags
        low = self._hashtagDistribution.lowHashtags
        medium = self._hashtagDistribution.mediumHashtags
        high = self._hashtagDistribution.highHashtags
        vhigh = self._hashtagDistribution.vhighHashtags

        low = sorted(low, key=lambda item: item[1])
        medium = sorted(medium, key=lambda item: item[1])
        high = sorted(high, key=lambda item: item[1])
        vhigh = sorted(vhigh, key=lambda item: item[1])

        lowAmount = 10
        mediumAmount = 10
        highAmount = 10
        # vhighAmount = 10

        # random.shuffle(low)
        # random.shuffle(medium)
        # random.shuffle(high)
        # random.shuffle(vhigh)

        result += low[:lowAmount]
        result += medium[:lowAmount-len(result)+10]
        result += high[:lowAmount+mediumAmount-len(result)+10]
        result += vhigh[:lowAmount+mediumAmount+highAmount-len(result)]

        random.shuffle(result)

        result = [f"#{tag[0]}" for tag in result]
        self.ui.sourceHashtags.setPlainText(' '.join(result))

    @Slot()
    def generateScores(self):
        user_likes = int(Table("users").select(where={"name": self.ui.currentText()}).first["daily_likes"])
        items = self._hashtags_table.select().items

        for item in items:
            if item["likes"]:
                like_ratio = int(item["likes"]) / user_likes
                self._hashtags_table.update(sets={"score": like_ratio}, where={"name": item["name"]})
            else:
                print(f"passing {item['name']}")


    @Slot()
    def collectionSelectionChanged(self):
        items = self.ui.hashtagCollections.selectedItems()
        collections = [f"{item.text()}" for item in items]

        records = self._collectionsTable.hashtags(collections)

        self._hashtagDistribution.clearTopLevelItems()
        for record in records:
            self._hashtagDistribution.addItem(record)


    @Slot()
    def hashtagManager(self):
        from hashtagmanagerdialog import HashtagManagerDialog
        hash = HashtagManagerDialog(self, self.ui.users.currentText())
        hash.ui.show()



    @Slot()
    def shuffleHashtags(self):
        hashtags = self.ui.sourceHashtags.toPlainText().replace("\n", " ").split(" ")
        random.shuffle(hashtags)
        hashtags = hashtags[:self.ui.numberOfHashtags.value()]
        hashtags = [hashtag if hashtag.startswith("#") else f"#{hashtag}" for hashtag in hashtags]
        self.ui.hashtagOutput.setPlainText(" ".join(hashtags))

    @Slot()
    def browse(self):
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder', "/media/Nextcloud/live/Familia/Inbox")
        self.ui.path.setText(folderpath)

    @Slot()
    def renameButtonClicked(self):
        directory = Path(self.ui.path.text())

        if directory.is_dir():
            self.renameDirectory(directory)
        elif directory.is_file():
            self.renameFile(directory)

    def renameDirectory(self, directory):
        count = len(list(directory.glob('*')))
        self.ui.fileProgress.setMaximum(count)

        for entry in sorted(directory.iterdir()):
            self.ui.fileProgress.setValue(self.ui.fileProgress.value() + 1)
            self.ui.currentFilename.setText(str(entry.name))

            if entry.name.startswith("__to_delete__"):
                self.log(f"Ignoring {entry}, since it's marked to be deleted.")
                continue

            self.renameFile(entry)
        self.ui.fileProgress.setValue(count)

    def renameFile(self, filename):
        extension = filename.suffix[1:].lower()
        if extension not in ["jpg", "jpeg", "png", "mov", "mpg", "mpeg", "mp4"]:
            return

        metadata = self.exif.get_metadata(filename)

        if len(metadata) > 1:
            self.log(f"{filename} has more then 1 metadata")

        metadata = metadata[0]

        new_filename = self.generate_filename(filename, metadata)

        if new_filename is None:
            return

        new_filename = f"{new_filename}.{extension}"
        # self.log(str(filename.parent / new_filename))

        # TODO: rename file here
        os.rename(filename, filename.parent / new_filename)

    def generate_filename(self, filename: Path, metadata: dict) -> str:
        # If it's a file generated by instagram, then mark it to remove
        if metadata.get("EXIF:Software") == "Instagram":
            self.log(f"Consider marking {filename} __to_delete__")
            return None
        if metadata.get("QuickTime:Model") == "DJI Pocket":
            date_result = metadata["QuickTime:CreateDate"]
            dt = datetime.strptime(date_result, "%Y:%m:%d %H:%M:%S")
            dt = dt + timedelta(hours=self.ui.dji_pocket.value())
            return dt.strftime("%Y%m%d_%H%M%S")
        elif metadata.get("QuickTime:Model") == "iPhone 12" and metadata["File:FileTypeExtension"].lower() == "mov":
            date_result = metadata["QuickTime:CreationDate"]
            if "+" in date_result:
                date_result = date_result.split("+")[0]
            dt = datetime.strptime(date_result, "%Y:%m:%d %H:%M:%S")
            dt = dt + timedelta(hours=self.ui.iphone_mov.value())
            return dt.strftime("%Y%m%d_%H%M%S")
        elif "Composite:SubSecDateTimeOriginal" in metadata:
            date_result = metadata["Composite:SubSecDateTimeOriginal"]
            date_result = date_result.split("+")[0]
            date_result, milisec = date_result.split(".")
            dt = datetime.strptime(date_result, "%Y:%m:%d %H:%M:%S")
            # dt = dt + timedelta(hours=self.ui.iphone_img.value())
            return dt.strftime(f"%Y%m%d_%H%M%S_{milisec}")
        elif "EXIF:DateTimeOriginal" in metadata:
            date_result = metadata["EXIF:DateTimeOriginal"]
            date_result = date_result.split("+")[0]
            dt = datetime.strptime(date_result, "%Y:%m:%d %H:%M:%S")
            # dt = dt + timedelta(hours=self.ui.iphone_img.value())
            return dt.strftime("%Y%m%d_%H%M%S")
        elif "QuickTime:CreateDate" in metadata:
            date_result = metadata["QuickTime:CreateDate"]
            date_result = date_result.split("+")[0]
            try:
                dt = datetime.strptime(date_result, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                self.log(f"Invalid date: {date_result}")
                return None
            # dt = dt + timedelta(hours=self.ui.iphone_img.value())
            return dt.strftime("%Y%m%d_%H%M%S")

        self.log(f"Incomplete metadata  (no creation date): {filename}\n{metadata}")
        return None

    def log(self, text: str):
        self.ui.output.setPlainText(self.ui.output.toPlainText() + "\n" + text)
        print(text)


if __name__ == "__main__":
    app = QApplication([])
    widget = MainWindow()
    # widget.show()
    widget.centralWidget().showNormal()
    sys.exit(app.exec())
