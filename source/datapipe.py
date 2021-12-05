from gmail_client import GmailClient
from pymongo import MongoClient
import time
from logger import logger
import traceback

CLIENT_SECRETS_FILE = "client_secret.json"
ACCESS_TOKEN_FILE = "token.pickle"


class DataPipe:
    def __init__(self, conn_string, test_run=False):
        self._gmail_client = GmailClient()
        self._mongodb_client = MongoClient(conn_string)
        self._db = self._mongodb_client.maximus
        self._downloaded = 0
        self._test_run = test_run

    # TODO: incremental sync
    # TODO: make this code multi-threaded or use async.
    # TODO: take label as input from user.
    def sync_data(self, label=None):
        try:
            all_labels = self._gmail_client.list_labels()['labels']
            cs410_label = next(filter(lambda x: x.get('name', "") == "cs410",
                                      all_labels))
            if cs410_label is None:
                raise Exception(f"Unable to find emails with label {label}")

            label_ids = ['INBOX', cs410_label['id']]

            self.update_sync_started(round(time.time()))
            messages, next_page_token = self._gmail_client.list_emails(
                                            label_ids=label_ids)
            self.store_messages(messages)
            # now paginate and fetch all emails.
            while (not self._test_run) and next_page_token:
                messages, next_page_token = self._gmail_client.list_emails(
                                                label_ids=label_ids,
                                                page_token=next_page_token)
                self.store_messages(messages)
            # Done updating.
            self.update_sync_finished(round(time.time()))
        except Exception as e:
            logger.error(traceback.format_exc())
            self.update_sync_failed(str(e))

    def update_sync_finished(self, end_time):
        self._db.sync_status.update_one(
            {'_id': 1},
            {
                '$set': {
                    'sync_finish_time': end_time,
                    'sync_status': "synced"
                }
            }
        )

    def update_sync_started(self, start_time):
        self._db.sync_status.update_one(
            {'_id': 1},
            {
                '$set': {
                    'sync_start_time': start_time,
                    'sync_status': "syncing",
                    'downloaded': self._downloaded,
                    'failure_reason': ""
                }
            },
            upsert=True
        )

    def update_sync_failed(self, error_msg):
        self._db.sync_status.update_one(
            {'_id': 1},
            {
                '$set': {
                    'sync_status': "failed",
                    'failure_reason':  error_msg
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
            logger.debug(f"Successfully stored message {msg['messageId']}")

        self._downloaded += len(messages)
        self._db.sync_status.update_one(
            {'_id': 1},
            {
                '$set': {
                    'downloaded': self._downloaded
                }
            }
        )


if __name__ == "__main__":
    # test code.
    dp = DataPipe("mongodb://localhost:27017")
    dp.sync_data(label="cs410")

