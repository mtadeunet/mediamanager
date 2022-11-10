from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QByteArray, QObject
import json
from threading import Thread
from queue import Empty, Queue
from functools import partial
import time

from PySide6.QtCore import QFile, Slot, Qt, QByteArray, QEventLoop

from database import HashtagTable, Table, CollectionsTable, UserTable

class Inssist:
    def __init__(self, userId) -> None:
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.finished)
        self.userId = userId

    def breakDownResponse(self, record) -> dict:
        parts = record.split(":")
        name = parts[0]
        hashtagId = parts[1]
        likes = parts[4]
        comments = parts[5]
        engagement = parts[6]
        suggestions = parts[7].split(",")

        return {
            "id": hashtagId,
            "name": name,
            "likes": likes,
            "comments": comments,
            "engagement": engagement,
            "suggestions": suggestions,
        }

    def processReply(self, response: dict):
        records = []
        if "tags" in response:
            for key, value in response["tags"].items():
                records.append(self.breakDownResponse(f"{key}:{value}"))
        elif "low" in response:
            for record in response["low"]:
                records.append(self.breakDownResponse(record))
            for record in response["medium"]:
                records.append(self.breakDownResponse(record))
            for record in response["high"]:
                records.append(self.breakDownResponse(record))
            for record in response["vhigh"]:
                records.append(self.breakDownResponse(record))

        return records

    def finished(self, reply: QNetworkReply):
        byteArray: QByteArray = reply.readAll()
        response = json.loads(byteArray.toStdString())

        print(f"inssist response: {response}")

        records = self.processReply(response)

        for record in records:
            reply.handler(record)


    def getHashtagData(self, hashtag: str, handler) -> QNetworkReply:
        request = QNetworkRequest(f"https://fc.inssist.com/api/v1/hashtag?id={self.userId}&tags={hashtag}")
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        reply: QNetworkReply = self.manager.get(request)
        reply.ignoreSslErrors()
        reply.handler = handler

        def errorHandler(error):
            print(error)
        reply.errorOccurred.connect(errorHandler)

        return reply


class InssistThread(Thread, QObject):
    __instance = None
    def get() -> "InssistThread":
        if not InssistThread.__instance:
            InssistThread.__instance = InssistThread()
        return InssistThread.__instance

    def __init__(self):
        super().__init__(name="Inssist Thread")
        self._queue = Queue()
        self.userId = "1781835001"
        self._hashtags_table = Table("hashtags")
        self._lastAutoRequestTime = time.time()
        self._currentUser = None

        self.start()

    def setCurrentUser(self, user):
        self._currentUser = user

    def recordBreakdown(self, record) -> dict:
        parts = record.split(":")
        name = parts[0]
        hashtagId = parts[1]
        likes = parts[4]
        comments = parts[5]
        engagement = parts[6]
        suggestions = parts[7].split(",")

        return {
            "hashtag_id": hashtagId,
            "name": name,
            "likes": likes,
            "comments": comments,
            "engagement": engagement,
            "suggestions": suggestions,
        }

    def processResponseData(self, response: dict) -> list:
        records = []
        if "tags" in response:
            for key, value in response["tags"].items():
                records.append(self.recordBreakdown(f"{key}:{value}"))
        elif "low" in response:
            for record in response["low"]:
                records.append(self.recordBreakdown(record))
            for record in response["medium"]:
                records.append(self.recordBreakdown(record))
            for record in response["high"]:
                records.append(self.recordBreakdown(record))
            for record in response["vhigh"]:
                records.append(self.recordBreakdown(record))

        return records


    def storeRecord(self, record: dict):
        user_likes = UserTable(self._currentUser).likes
        if "last_update" not in record:
            record["last_update"] = int(time.time())

        database_record = record.copy()
        if database_record["suggestions"]:
            database_record["suggestions"] = ",".join(database_record["suggestions"])

        if database_record["likes"]:
            database_record["score"] = int(database_record["likes"]) / user_likes

        if self._hashtags_table.exists(where={"name": record["name"]}):
            self._hashtags_table.update(sets=database_record, where={"name": record["name"]})
        else:
            self._hashtags_table.insert(values=record)

        # for suggestion in record["suggestions"]:
        #     if not self._hashtags_table.exists({"name": suggestion}):
        #         self._hashtags_table.insert({"name": suggestion})

    # def invalidateRecord(self, name):
        # self._hashtags_table.update(sets={"last_update": 9999999999}, where={"name": name})

    def responseHandler(self, request, reply):
        byteArray: QByteArray = reply.readAll()
        response = json.loads(byteArray.toStdString())

        if response["status"] == "ok":
            records = self.processResponseData(response)
        elif response["status"] == "too-many-requests":
            # wait 2 hours to cool down
            self._lastAutoRequestTime = time.time() + (60*60*2)
            return
        else:
            print(response)
            return

        responseRecordNames = [record["name"] for record in records]

        for name in request["name"].split(','):
            if name not in responseRecordNames:
                print(f"invalidating hashtag: {name}")
                records.append({
                    "name": name,
                    "hashtag_id": None,
                    "likes": None,
                    "comments": None,
                    "engagement": None,
                    "score": None,
                    "suggestions": None,
                    "last_update": 9999999999,
                })
                # self.invalidateRecord(name)

        for record in records:
            if request["updateDatabase"]:
                self.storeRecord(record)

            if request["callback"]:
                request["callback"](record)

    def run(self):
        manager = QNetworkAccessManager()

        while True:
            try:
                item = self._queue.get(timeout=0.5)
            except Empty as e:
                QEventLoop().processEvents()
                # if self._lastAutoRequestTime + 30 < time.time():
                #     hashtags = CollectionsTable().updatableHashtags()
                #     if not hashtags:
                #         hashtags = HashtagTable().randomUpdatable()
                #     self.requestHashtag(hashtags)

                # if self._lastAutoRequestTime + 30 < time.time():
                #     self._lastAutoRequestTime = time.time()
                #     hashtags = self._hashtags_table.select(where=f"last_update < {time.time() - (60*60*24*30)}", limit=30).items
                #     if hashtags:
                #         hashtags = [str(hashtag["name"]) for hashtag in hashtags]
                #         self.requestHashtag(hashtags)
                continue

            request = QNetworkRequest(f"https://fc.inssist.com/api/v1/hashtag?id={self.userId}&tags={item['name']}")
            request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
            reply: QNetworkReply = manager.get(request)
            reply.ignoreSslErrors()

            reply.finished.connect(partial(self.responseHandler, item, reply))


    def requestHashtag(self, name:str|list, callback=None, updateDatabase=True):
        if isinstance(name, list):
            name = ",".join(name)

        names = [name[i:i + 100] for i in range(0, len(name), 100)]

        for name in names:
            self._queue.put({
                "name": name,
                "callback": callback,
                "updateDatabase": updateDatabase,
            })
