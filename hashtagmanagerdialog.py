import os
import json
from pathlib import Path
import time
from functools import partial
from threading import Thread
from PySide6.QtWidgets import (
    QDialog,
    QInputDialog,
    QTableWidgetItem,
    QCheckBox,
    QListWidgetItem,
    QTableWidgetSelectionRange,
    QPushButton,
    QTableWidget,
    QProgressDialog,
    QProgressBar,
    QToolButton,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Slot, Qt, QByteArray, QSignalBlocker, QEvent, QModelIndex, QObject, QEventLoop
from PySide6.QtGui import QMouseEvent, QIcon


from database import Table, DatabaseExecution, DatabaseManager, CollectionsTable, HashtagTable, CollectionHashtagsTable, UserTable
from Inssist import InssistThread
import common


class HashtagManagerDialog(QDialog):

    class TableView(QObject):
        def __init__(self, parent, tableWidget: QTableWidget) -> None:
            super().__init__(parent)
            self._tableWidget: QTableWidget = tableWidget

        @property
        def table(self):
            return self._tableWidget

        def clear(self):
            self.table.setRowCount(0)

        def blockSignals(self, value):
            self.table.blockSignals(value)

        def _createItem(self, name, color, data=None):
            result = QTableWidgetItem()
            result.setData(Qt.DisplayRole, name)
            result.setBackground(color)
            if data:
                # result.setData(Qt.ItemDataRole, str(data))
                result.record = data
            return result

        def updateItem(self, index, record):
            pass

        def _setItem(self, index, record):
            pass

        def addRow(self, record):
            index = self.table.rowCount()
            self.table.insertRow(index)

            self._setItem(index, record)

        def updateRow(self, record):
            item = self.table.findItems(record["name"], Qt.MatchExactly)

            if not item:
                return

            item = item[0]
            index = self.table.indexFromItem(item)
            self.updateItem(index.row(), record)

        def selectedItems(self):
            return self.table.selectedItems()

        def selectedRecords(self) -> dict:
            indexes = self.table.selectedIndexes()

            indexes = [index.row() for index in indexes]
            indexes = list(set(indexes))
            result = []
            for index in indexes:
                result.append(self.table.item(index, 1).record)
            return result

        def allRecords(self) -> list:
            result = []
            for index in range(0, self.table.rowCount()):
                result.append(self.table.item(index, 1).record)
            return result

        def removeHashtag(self, name):
            items = self.table.findItems(name, Qt.MatchExactly)
            index = self.table.indexFromItem(items[0])
            self.table.removeRow(index.row())

    class SuggestedHashtags(TableView):
        def __init__(self, parent) -> None:
            super().__init__(parent, parent.ui.hashtagTableWidget)
            self.table.setColumnWidth(0, 32)

        def updateItem(self, index, record):
            score = common.defineScore(record, UserTable(self.parent().currentUser))
            color = common.defineRowColor(record, score)
            self.table.setItem(index, 1, self._createItem(record["name"], color, record))
            self.table.setItem(index, 2, self._createItem(record["likes"], color))
            self.table.setItem(index, 3, self._createItem(record["comments"], color))
            self.table.setItem(index, 4, self._createItem(record["engagement"], color))
            self.table.setItem(index, 5, self._createItem(score, color))

        def _setItem(self, index, record):
            score = common.defineScore(record, UserTable(self.parent().currentUser))

            color = common.defineRowColor(record, score)

            self.table.setItem(index, 1, self._createItem(record["name"], color, record))
            self.table.setItem(index, 2, self._createItem(record["likes"], color))
            self.table.setItem(index, 3, self._createItem(record["comments"], color))
            self.table.setItem(index, 4, self._createItem(record["engagement"], color))
            self.table.setItem(index, 5, self._createItem(score, color))

            if self.table.cellWidget(index, 6) is None:
                button = QToolButton()
                button.setIcon(QIcon.fromTheme("download"))
                button.clicked.connect(partial(self.parent().fetchHashtagFromTable, record["name"]))
                self.table.setCellWidget(index, 5, button)
                self.table.setColumnWidth(5, button.height())

            if self.table.cellWidget(index, 7) is None:
                button = QToolButton()
                button.setIcon(QIcon.fromTheme("process-stop") if score == '-' else QIcon.fromTheme("project_add"))
                button.setEnabled(score != '-')
                button.clicked.connect(partial(self.parent().addToCollection, record["name"]))
                self._tableWidget.setCellWidget(index, 6, button)
                self.table.setColumnWidth(6, button.height())

        def deactivateInCollection(self, hashtags: dict):
            for index in range(0, self.table.rowCount()):
                record = self.table.item(index, 1).record
                score = common.defineScore(record, UserTable(self.parent().currentUser))
                button = self.table.cellWidget(index, 6)
                isInCollection = record["name"] in hashtags
                enabled = score != '-' and not isInCollection
                button.setIcon(QIcon.fromTheme("project_add") if enabled else QIcon.fromTheme("process-stop"))
                button.setEnabled(enabled)
                if isInCollection:
                    item = QTableWidgetItem()
                    item.setIcon(QIcon().fromTheme("checkmark"))
                    self.table.setItem(index, 0, item)
                else:
                    self.table.setItem(index, 0, QTableWidgetItem())



    class CollectionHashtags(TableView):
        def __init__(self, parent) -> None:
            super().__init__(parent, parent.ui.collectionHashtags)
            self.parent().ui.collectionHashtags.itemSelectionChanged.connect(self.parent().collectionTagsSelection)
            self.table.setColumnWidth(0, 32)
            self._collection_hashtags_table = CollectionHashtagsTable()

        def updateItem(self, index, record):
            score = common.defineScore(record, UserTable(self.parent().currentUser))
            color = common.defineRowColor(record, score)

            item = QTableWidgetItem()
            item.setIcon(QIcon().fromTheme("checkmark"))
            self.table.setItem(index, 0, item)

            self.table.setItem(index, 1, self._createItem(record["name"], color, record))
            self.table.setItem(index, 2, self._createItem(record["likes"], color))
            self.table.setItem(index, 3, self._createItem(record["comments"], color))
            self.table.setItem(index, 4, self._createItem(record["engagement"], color))
            self.table.setItem(index, 5, self._createItem(score, color))

            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Checked if record["collection_favorite"] else Qt.Unchecked)
            checkbox.stateChanged.connect(partial(self._favoriteChanged, record))
            self.table.setCellWidget(index, 6, checkbox)

        def _setItem(self, index, record):
            # score = record["likes"] / UserTable(self.parent().currentUser).likes
            score = common.defineScore(record, UserTable(self.parent().currentUser))
            color = common.defineRowColor(record, score)

            self.table.setItem(index, 1, self._createItem(record["name"], color, record))
            self.table.setItem(index, 2, self._createItem(record["likes"], color))
            self.table.setItem(index, 3, self._createItem(record["comments"], color))
            self.table.setItem(index, 4, self._createItem(record["engagement"], color))
            self.table.setItem(index, 5, self._createItem(score, color))

            if not self.table.cellWidget(index, 6):
                button = QToolButton()
                button.setIcon(QIcon.fromTheme("delete"))
                button.clicked.connect(partial(self.parent().removeHashtagFromCollection, record["name"]))
                self.table.setCellWidget(index, 5, button)
                self.table.setColumnWidth(5, button.height())

                checkbox = QCheckBox()
                checkbox.setCheckState(Qt.Checked if record["collection_favorite"] else Qt.Unchecked)
                checkbox.stateChanged.connect(partial(self._favoriteChanged, record))
                self.table.setCellWidget(index, 6, checkbox)

        def _favoriteChanged(self, record, state):
            self._collection_hashtags_table.update(sets={"favorite": state == Qt.Checked}, where={"id": record["collection_hashtag_id"]})


    def __init__(self, currentUser, parent) -> None:
        super().__init__(parent)

        self._hashtags_table = HashtagTable()
        self._collections_table = CollectionsTable()
        self._collection_hashtags_table = CollectionHashtagsTable()
        self.inssist = InssistThread.get()
        self._currentUser = currentUser

        self.load_ui()

    def load_ui(self):
        ui_file = QFile("hashtagManagerDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(ui_file, self)  # self.ui same as self.centralWidget()
        ui_file.close()

        self.ui.addCollectionButton.clicked.connect(self.add_collection)
        self.ui.removeCollectionButton.clicked.connect(self.remove_collection)
        self.ui.hashtagLookup.clicked.connect(self.hashtagLookup)


        self.ui.collections.itemSelectionChanged.connect(self.collectionChanged)
        for item in self._collections_table.select().items:
            self.ui.collections.addItem(item["name"])
        self.ui.collections.clearSelection()

        self.ui.suggestedSearch.textChanged.connect(self.searchTextChanged)

        self.ui.requestCollectionMissingTags.clicked.connect(self.requestCollectionMissingTags)
        self.ui.fetchSuggestions.clicked.connect(self.fetchSuggestions)
        self.ui.fetchCollectionHashtags.clicked.connect(self.fetchCollectionHashtags)
        self.ui.forceTagsInCollection.clicked.connect(self.forceTagsInCollection)

        self._collectionHashtags = HashtagManagerDialog.CollectionHashtags(self)
        self._suggestedHashtags = HashtagManagerDialog.SuggestedHashtags(self)

    @property
    def currentUser(self):
        return self._currentUser

    @Slot()
    def forceTagsInCollection(self):
        collection = self.ui.collections.currentItem().text()
        hashtags = self.ui.collectionEdit.text().replace("#", "").split(" ")
        hashtags_to_request = []
        for hashtag in hashtags:
            if self._collection_hashtags_table.exists(f"collection='{collection}' AND hashtag='{hashtag}'"):
                continue

            if not self._hashtags_table.exists(f"name='{hashtag}'"):
                self._hashtags_table.insert(values={"name": hashtag})
                hashtags_to_request.append(hashtag)

            self._collection_hashtags_table.insert(values={
                "collection": collection,
                "hashtag": hashtag,
                "favorite": 1
            })



    @Slot()
    def fetchCollectionHashtags(self):
        collection = self.ui.collections.currentItem().text()
        records = self._collections_table.hashtags(collection)
        hashtags = [record["name"] for record in records]

        self.inssist.requestHashtag(hashtags, self.hashtagHandler)

    @Slot()
    def fetchSuggestions(self):
        records = self._suggestedHashtags.allRecords()
        hashtags = [record["name"] for record in records]
        self.inssist.requestHashtag(hashtags, self.hashtagHandler)

    @Slot()
    def requestCollectionMissingTags(self):
        records = self._collectionHashtags.allRecords()
        hashtags = [record["name"] for record in records]
        self.inssist.requestHashtag(hashtags, self.hashtagHandler)

    @Slot()
    def collectionTagsSelection(self):
        records = self._collectionHashtags.selectedRecords()
        suggestions = []

        for record in records:
            if record["suggestions"]:
                suggestions += record["suggestions"].split(',')

        self._suggestedHashtags.clear()

        quoted_suggestions = ','.join(f"'{suggestion}'" for suggestion in suggestions)

        records = self._hashtags_table.select(where=f"name in ({quoted_suggestions})").items
        mapped_records = {}
        for record in records:
            mapped_records[record["name"]] = record
        for suggestion in suggestions:
            if suggestion in mapped_records:
                record = mapped_records[suggestion]
            else:
                record = self._hashtags_table.addEmpty(suggestion)

            self._suggestedHashtags.addRow(record)

        # deactivate add buttons for already in the collection
        records = self._collectionHashtags.allRecords()
        self._suggestedHashtags.deactivateInCollection([record["name"] for record in records])

    @Slot()
    def addToCollection(self, name: str):
        collection = self.ui.collections.currentItem().text()
        if self._collection_hashtags_table.exists(where={"collection": collection, "hashtag": name}):
            return

        self._collection_hashtags_table.insert(values={
            "collection": collection,
            "hashtag": name
        })


        record = self._hashtags_table.select(where={"name": name}).first
        self._collectionHashtags.addRow(record)

        records = self._collectionHashtags.allRecords()
        self._suggestedHashtags.deactivateInCollection([record["name"] for record in records])


    @Slot()
    def removeHashtagFromCollection(self, name: str):
        collection = self.ui.collections.currentItem().text()
        self._collection_hashtags_table.delete(where={"collection": collection, "hashtag": name})
        self._collectionHashtags.removeHashtag(name)

        records = self._collectionHashtags.allRecords()
        self._suggestedHashtags.deactivateInCollection([record["name"] for record in records])

    @Slot()
    def fetchHashtagFromTable(self, hashtag):
        self.inssist.requestHashtag(hashtag, self.hashtagHandler)

    def hashtagHandler(self, record: dict):
        record =self._hashtags_table.select(where={"name": record["name"]}).first

        self._collectionHashtags.updateRow(record)
        self._suggestedHashtags.updateRow(record)

        records = self._collectionHashtags.allRecords()
        self._suggestedHashtags.deactivateInCollection([record["name"] for record in records])


    @Slot()
    def hashtagLookup(self):
        self.inssist.requestHashtag(self.ui.suggestedSearch.text(), self.hashtagHandler)

    @Slot()
    def searchTextChanged(self):
        for index in range(0, self.ui.hashtagTableWidget.rowCount()):
            item = self.ui.hashtagTableWidget.item(index, 0)
            self.ui.hashtagTableWidget.setRowHidden(index, self.ui.suggestedSearch.text() not in item.text())


    @Slot()
    def collectionChanged(self):
        item = self.ui.collections.currentItem()
        collection_hashtags = self._collection_hashtags_table.select(where={"collection": item.text()}).items

        self._collectionHashtags.blockSignals(True)
        self._collectionHashtags.clear()

        for index in range(0, len(collection_hashtags)):
            collection_hashtag_record = collection_hashtags[index]
            record = self._hashtags_table.select(where={"name": collection_hashtag_record["hashtag"]}).first

            if record is None:
                continue

            record["collection_hashtag_id"] = collection_hashtag_record["id"]
            record["collection_name"] = collection_hashtag_record["collection"]
            record["collection_favorite"] = collection_hashtag_record["favorite"]
            self._collectionHashtags.addRow(record)
        self._collectionHashtags.blockSignals(False)


    @Slot()
    def add_collection(self):
        collection_name, _ = QInputDialog.getText(self, "Insert Collection Name", "Collection:")

        collections_table = Table("collections")
        if not collections_table.select(where={"name": collection_name}).first:
            collections_table.insert({"name": collection_name})
            self.ui.collections.addItem(collection_name)

    @Slot()
    def remove_collection(self):
        item: QListWidgetItem = self.ui.collections.takeItem(self.ui.collections.currentRow())
        if item:
            Table("collections").delete(where={"name": item.text()})

