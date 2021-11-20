from gmail_client import GmailClient
from pymongo import MongoClient
import time

CLIENT_SECRETS_FILE = "client_secret.json"
ACCESS_TOKEN_FILE = "token.pickle"


class DataPipe:
    def __init__(self, credentials, conn_string):
        self._gmail_client = GmailClient(credentials)
        self._mongodb_client = MongoClient(conn_string)
        self._db = self._mongodb_client.maximus

    # TODO: incremental sync
    # TODO: make this code multi-threaded or use async.
    def sync_data(self):
        self.update_sync_started(round(time.time()))
        messages, page_token = self._gmail_client.list_emails()
        self.store_messages(messages)
        # now paginate and fetch all emails.
        while page_token:
            messages = self._gmail_client.list_emails(page_token)
            # all_messages.extend(messages)
            self.store_messages(messages)
        self.update_sync_finished(round(time.time()))

    def update_sync_finished(self, end_time):
        self._db.sync_status.update_one(
            {'_id': 1},
            {
                '$set': {
                    'sync_start_time': end_time,
                    'sync_status': "synced"
                }
            }
        )

    def update_sync_started(self, start_time):
        db = self._mongodb_client.maximus
        db.sync_status.update_one(
            {'_id': 1},
            {
                '$set': {
                    'sync_start_time': start_time,
                    'sync_status': "syncing"
                }
            },
            upsert=True
        )

    def store_messages(self, messages):
        for msg in messages:
            # we make the message's id as _id of document
            # in mongodb.
            new_msg = {
                "_id": msg['messageId'],
            }
            new_msg.update(msg)
            # insert new, but replace in case we download the
            # message again, message contents don't change.
            self._db.emails.replace_one({"_id": new_msg["_id"]},
                                        new_msg,
                                        upsert=True)


if __name__ == "__main__":
    # test code.
    import pickle
    credential = None
    with open(ACCESS_TOKEN_FILE, "rb") as tf:
        cred = pickle.load(tf)
    dp = DataPipe(cred, "mongodb://localhost:27017")
    dp.sync_data()
