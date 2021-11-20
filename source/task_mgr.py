from concurrent.futures import ThreadPoolExecutor
from datapipe import DataPipe
import pickle

ACCESS_TOKEN_FILE = "token.pickle"


def data_sync_task():
    with open(ACCESS_TOKEN_FILE, "rb") as tf:
        cred = pickle.load(tf)
    dp = DataPipe(cred, "mongodb://localhost:27017")
    dp.sync_data()


def data_analyze_task():
    pass


class TaskMgr:
    def __init__(self):
        self._exe = ThreadPoolExecutor(max_workers=5)

    def execute_task(self, task):
        self._exe.submit(task)


def test_task():
    print("Hi, I am a test task.")


if __name__ == "__main__":
    tm = TaskMgr()
    tm.execute_task(test_task)


