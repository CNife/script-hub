import os
import sys

from redis.client import Redis
from rq import SimpleWorker, Worker
from rq.timeouts import TimerDeathPenalty

from script_hub.settings import settings
from script_hub.task_queue import queue


def run():
    log_file = open(settings.WORKER_LOG_PATH, "a", encoding="UTF-8")
    sys.stdout = log_file
    sys.stderr = log_file

    worker_class = get_worker_class()
    worker = worker_class([queue], connection=Redis.from_url(settings.REDIS_URL))

    settings.WORKER_NAME_PATH.write_text(worker.name, encoding="UTF-8")

    worker.work()


def get_worker_class():
    if settings.DEBUG_MODE:
        if not hasattr(os, "fork"):

            class WindowsWorker(SimpleWorker):
                death_penalty_class = TimerDeathPenalty

            worker_class = WindowsWorker
        else:
            worker_class = SimpleWorker
    else:
        worker_class = Worker
    return worker_class


if __name__ == "__main__":
    run()
