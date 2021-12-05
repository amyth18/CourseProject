from pymongo import MongoClient
import pandas as pd

# TODO: from env.
conn_string = "mongodb://localhost:27017"


class MongoDBClient:
    def __init__(self):
        self._mongodb_client = MongoClient(conn_string)
        self._db = self._mongodb_client.maximus

    def get_sync_status(self):
        cur = self._db.sync_status.find({"_id": 1})
        return cur.next()

    def get_analyze_status(self):
        cur = self._db.analyze_status.find({"_id": 1})
        return cur.next()

    def get_all_messages(self):
        cursor = self._db.emails.find({})
        return pd.DataFrame(list(cursor))

    def get_message_counts(self, topic):
        all_count = self._db.emails.find(
            {
                "topics": {"$all": [topic]}
            }
        ).count()
        unread_count = self._db.emails.find({
            "$and": [
                {"topics": {"$all": [topic]}},
                {"labels": {"$all": ["UNREAD"]}}
            ]
        }
        ).count()
        return all_count, unread_count

    def get_db_handle(self):
        return self._db


def to_messages_csv(mc):
    df = mc.get_all_messages()
    df.loc[df.text == "", 'text'] = df.loc[df.text == ""]['subject']
    df.loc[df.text.isna(), 'text'] = df[df.text.isna()]['subject']
    df.to_csv("emails.csv")


if __name__ == "__main__":
    mdb = MongoDBClient()
    a, b = mdb.get_message_counts("Label_8904163162243193684")
    print(f"{a}, {b}")

