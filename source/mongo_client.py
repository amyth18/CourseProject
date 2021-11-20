from pymongo import MongoClient

# TODO: from env.
conn_string = "mongodb://localhost:27017"


class MongoDBClient:
    def __init__(self):
        self._mongodb_client = MongoClient(conn_string)
        self._db = self._mongodb_client.maximus

    def get_sync_status(self):
        cur = self._db.sync_status.find({"_id": 1})
        return cur.next()

