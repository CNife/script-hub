import subprocess
import sys
from typing import Iterator, Annotated

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, StreamingResponse

app = FastAPI()


@app.get("/")
def index():
    return FileResponse("web/index.html")


@app.get("/run")
def run(params: Annotated[str, Query()]):
    return StreamingResponse(execute_script([params]), media_type="text/event-stream")


def execute_script(params: list[str]) -> Iterator[str]:
    process = subprocess.Popen(
        [sys.executable, "-m", "test_script.echo"] + params,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="UTF-8",
    )
    for line in process.stdout:
        yield f"data: {line}\n\n"

    code = process.wait()
    if code != 0:
        yield f"data: Failed, code: {code}\n\n"
    else:
        yield f"event: done\ndata: done\n\n"
