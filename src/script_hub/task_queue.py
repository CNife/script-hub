import subprocess
import sys
from pathlib import Path

from redis.client import Redis
from rq import Queue, Worker
from rq.command import send_shutdown_command

from script_hub.settings import settings

queue = Queue(connection=Redis.from_url(settings.REDIS_URL))


def start_worker() -> subprocess.Popen:
    worker_script = Path(__file__).with_name("worker.py")
    return subprocess.Popen([sys.executable, worker_script])


def stop_worker() -> bool:
    if not settings.WORKER_NAME_PATH.exists():
        return False

    worker_name = settings.WORKER_NAME_PATH.read_text("UTF-8")
    if worker_name not in Worker.all(queue.connection):
        return False

    send_shutdown_command(queue.connection, worker_name)
    return True
