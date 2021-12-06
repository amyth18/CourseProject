from concurrent.futures import ThreadPoolExecutor
from datapipe import DataPipe
from topic_model import TopicModel
from mongo_client import MongoDBClient
import time
import traceback
import logger


def update_analyze_finished(mdb, end_time):
    mdb.analyze_status.update_one(
        {'_id': 1},
        {
            '$set': {
                'analyze_finish_time': end_time,
                'analyze_status': "completed"
            }
        }
    )


def update_analyze_started(mdb, start_time):
    mdb.analyze_status.update_one(
        {'_id': 1},
        {
            '$set': {
                'analyze_start_time': start_time,
                'analyze_status': "analyzing",
                'failure_reason': ""
            }
        },
        upsert=True
    )


def update_analyze_failed(mdb, error_msg):
    mdb.analyze_status.update_one(
        {'_id': 1},
        {
            '$set': {
                'analyze_status': "failed",
                'failure_reason':  error_msg
            }
        }
    )


def data_sync_task():
    dp = DataPipe()
    # only look for messages in INBOX
    dp.sync_data(label="cs410")


def analyze_data_task():
    mdb = MongoDBClient()
    try:
        update_analyze_started(mdb.get_db_handle(), round(time.time()))
        tpm = TopicModel()
        tpm.discover()
        update_analyze_finished(mdb.get_db_handle(), round(time.time()))
    except Exception as e:
        logger.error(traceback.format_exc())
        update_analyze_failed(mdb.get_db_handle(), str(e))


class TaskMgr:
    def __init__(self):
        self._exe = ThreadPoolExecutor(max_workers=5)

    # TODO: thread reaping for errors?
    def execute_task(self, task):
        self._exe.submit(task)
