import time
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlRecord, QSqlTableModel, QSqlDriver

class DatabaseManager:
    __instance = None
    @staticmethod
    def get():
        if not DatabaseManager.__instance:
            DatabaseManager.__instance = DatabaseManager()
        return DatabaseManager.__instance

    def __init__(self) -> None:
        self.database = QSqlDatabase.addDatabase("QSQLITE")
        self.database.setDatabaseName("mediarename.db")
        self.database.open()

        QSqlQuery("""
            CREATE TABLE IF NOT EXITS "hashtags2" (
                "id"	INTEGER,
                "name"	TEXT NOT NULL,
                "posts"	INTEGER,
                "average_likes"	INTEGER,
                "average_comments"	INTEGER,
                "trend"	REAL,
                "last_data_update"	TEXT,
                "last_trend_update"	TEXT,
                PRIMARY KEY("id" AUTOINCREMENT)
            )""")

        QSqlQuery("""
            CREATE TABLE IF NOT EXITS "collections" (
                "id"	INTEGER,
                "name"	TEXT NOT NULL,
                "referrals"	TEXT,
                PRIMARY KEY("id" AUTOINCREMENT)
            )""")

        QSqlQuery("""
            CREATE TABLE IF NOT EXITS "users" (
                "id"	INTEGER,
                "name"	TEXT NOT NULL,
                "daily_likes"	INTEGER,
                PRIMARY KEY("id" AUTOINCREMENT)
            )""")

        QSqlQuery("""
            CREATE TABLE "hashtags" (
                "id"	INTEGER,
                "name"	TEXT NOT NULL,
                "likes"	INTEGER,
                "comments"	INTEGER,
                "engagement"	INTEGER,
            	"score"	INTEGER DEFAULT 0,
            	"suggestions"	TEXT,
            	"last_update"	INTEGER DEFAULT 0,
                PRIMARY KEY("id","name")
            )""")

        QSqlQuery("""
            CREATE TABLE "collection_hashtags" (
                "id"	INTEGER,
                "collection" TEXT NOT NULL,
                "hashtag"	TEXT NOT NULL,
            	"favorite"	INTEGER DEFAULT 0,
                PRIMARY KEY("id" AUTOINCREMENT)
            )""")


class DatabaseExecution:
    def __init__(self, sql, params=[]) -> None:
        self._sql = sql
        self._query = QSqlQuery(DatabaseManager.get().database)
        self._query.prepare(sql)
        self._params = params

        has_placeholders = self._query.driver().hasFeature(QSqlDriver.NamedPlaceholders)

        for param in params:
            self._query.addBindValue(param)

        print(self._sql)
        # print(self._query.boundValues())

        if not self._query.exec():
            raise Exception(f"Database Error: {self._query.lastError().text()}\n{self._sql}\n{self._params}")

    @property
    def items(self) -> list:
        result = []

        while self._query.next():
            record = self._query.record()
            new_record = {}
            for index in range(0, record.count()):
                new_record[record.fieldName(index)] = None if record.isNull(index) else record.value(index)
            result.append(new_record)
        return result

    @property
    def first(self) -> dict|None:
        items = self.items
        return items[0] if items else None

    @property
    def rows_affected(self) -> int:
        return self._query.numRowsAffected()

    @property
    def last_insert_id(self) -> int:
        return self._query.lastInsertId()

class DatabaseTableBase:
    def __init__(self) -> None:
        DatabaseManager.get()

    def __process_where(self, where):
        if not where:
            return "", []
        if isinstance(where, str):
            return f"WHERE {where}", []
        if isinstance(where, list):
            return f"WHERE {' AND '.join(where)}", []
        result = ""
        params = []
        for key in where.keys():
            result = f"{result} {'AND' if result else 'WHERE'} {key}=?"
            params.append(where[key])
        return result, params

    def __process_order(self, order: list):
        if not order:
            return ""
        result = ""
        for col in order:
            result = f"{result} {'AND' if result else 'ORDER BY'} {col}"
        return result

    def select(self, table: str, cols: str='*', where: dict=None, order: list=None, limit:int=None) -> DatabaseExecution:
        params = []
        where_params = []
        limit_str = f"LIMIT {limit}" if limit else ""
        where_str, where_params = self.__process_where(where)
        order_str = self.__process_order(order)

        sql = f"SELECT {cols} FROM `{table}` {where_str} {order_str} {limit_str}"

        params += where_params

        return DatabaseExecution(sql, params)

    def insert(self, table, values:dict) -> DatabaseExecution:
        keys = [key for key in values.keys()]
        cols = ','.join(keys)
        col_values = ','.join(['?' for index in range(0, len(keys))])

        sql = f"INSERT INTO `{table}` ({cols}) VALUES ({col_values})"
        return DatabaseExecution(sql, [values[key] for key in keys])

    def update(self, table, sets:dict, where:dict) -> DatabaseExecution:
        params = [sets[key] for key in sets.keys()]
        where_params = []
        if isinstance(where, str):
            where_str = f"WHERE {where}"
        else:
            where_str, where_params = self.__process_where(where)
        params += where_params

        sets = ",".join([f"{key}=?" for key in sets.keys()])

        sql = f"UPDATE `{table}` SET {sets} {where_str}"

        return DatabaseExecution(sql, params)

    def delete(self, table, where) -> DatabaseExecution:
        where_params = []
        if isinstance(where, str):
            where_str = f"WHERE {where}"
        else:
            where_str, where_params = self.__process_where(where)
        sql = f"DELETE FROM `{table}` {where_str}"

        return DatabaseExecution(sql, where_params)

class Table:
    def __init__(self, table: str) -> None:
        self._table_name = table
        self._table_object = DatabaseTableBase()

    def exists(self, where:str=None):
        return self.select(where=where).first is not None

    def select(self, cols: str='*', where: str=None, order: str=None, limit=None) -> DatabaseExecution:
        return self._table_object.select(self._table_name, cols, where, order, limit)

    def insert(self, values: dict) -> DatabaseExecution:
        return self._table_object.insert(self._table_name, values)

    def update(self, sets:dict, where=None) -> DatabaseExecution:
        return self._table_object.update(self._table_name, sets, where)

    def delete(self, where:str=None) -> DatabaseExecution:
        return self._table_object.delete(self._table_name, where)


class HashtagTable(Table):
    def __init__(self) -> None:
        super().__init__("hashtags")

    def addEmpty(self, name):
        id = self.insert(values={"name": name}).last_insert_id
        return self.select(where={"id": id}).first

    def suggestions(self, name):
        if isinstance(name, list):
            name = [f"'{n}'" for n in name]
        else:
            name = [f"'{name}'"]

        suggestions = self.select(cols="suggestions", where=f"name in ({','.join(name)})").items

        result = []
        for suggestion in suggestions:
            if suggestion["suggestions"]:
                result += suggestion["suggestions"].split(',')
        result = list(set(result))
        result.sort()
        return result

    # def randomUpdatable(self, limit=30):
    #     begin = list("01234567890abcdefghijklmnopqrstuvxywz")
    #     import random
    #     rand = random.randint(0, len(begin))

    #     records = HashtagTable().select(where=f"name like '{begin[rand]}%' last_update < 9999999999 and last_update < {time.time() - (60*60*24*30)}", limit=limit).items

    #     return [record["name"] for record in records]


class CollectionHashtagsTable(Table):
    def __init__(self) -> None:
        super().__init__("collection_hashtags")

    def hashtags(self, collections: str|list):
        if isinstance(collections, str):
            collections = collections.split(",")

        collections = [f"'{collection}'" for collection in collections]

        return [record["hashtag"] for record in self.select(where=f"collection in ({','.join(collections)})").items]

class CollectionsTable(Table):
    _cache = None

    def __init__(self) -> None:
        super().__init__("collections")

    def cacheGetCollectionSuggestions(self, collection):
        result = []
        for hashtag, suggestions in CollectionsTable._cache[collection].items():
            result += suggestions
        result = list(set(result))
        result.sort()
        return result

    def collections(self):
        return [record["name"] for record in self.select(order=["name"]).items]

    def hashtags(self, collections: str|list):
        records = CollectionHashtagsTable().hashtags(collections)
        quoted_hashtags = [f"'{record}'" for record in records]

        return HashtagTable().select(where=f"name in ({','.join(quoted_hashtags)})").items

        # result = []
        # for hashtag in hashtags:
        # result = []

        # for hashtag in hashtags:
        #     result += HashtagTable().suggestions(hashtag)

        # return result

    def referrals(self, collection):
        return self.select(where={"name": collection}).first["referrals"].split(" ")

    def updatableHashtags(self, collections=None, limit=30):
        collectionHashtags = []

        if not collections:
            collections = self.collections()

        collectionHashtags += self.collectionHashtags(collections)

        suggestions = HashtagTable().suggestions(collectionHashtags)

        # collectionHashtags = [f"'{hashtag}'" for hashtag in collectionHashtags]

        records = HashtagTable().select(where=f"name in ({','.join(collectionHashtags)}) AND last_update < 9999999999 and last_update < {time.time() - (60*60*24*30)}", limit=limit).items
        return [record["name"] for record in records]


class UsersTable(Table):
    def __init__(self) -> None:
        super().__init__("users")

class UserTable(Table):
    _users = {}
    def __init__(self, user) -> None:
        super().__init__("users")
        self._user = user
        if user not in UserTable._users:
            UserTable._users[user] = self.select(where={"name": user}).first

    @property
    def likes(self) -> int:
        return UserTable._users[self._user]["daily_likes"]
