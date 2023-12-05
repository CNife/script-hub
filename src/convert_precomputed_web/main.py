import os.path
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
def run(
    image_path: Annotated[str, Query(alias="imagePath")],
    output_directory: Annotated[str, Query(alias="outputDirectory")],
    resolution_x: Annotated[int, Query(alias="resolutionX")],
    resolution_y: Annotated[int, Query(alias="resolutionY")],
    resolution_z: Annotated[int, Query(alias="resolutionZ")],
    write_block_size: Annotated[int, Query(alias="writeBlockSize")],
    resume: Annotated[bool, Query(alias="resume")],
):
    return StreamingResponse(
        execute_script(
            image_path, output_directory, resolution_x, resolution_y, resolution_z, write_block_size, resume
        ),
        media_type="text/event-stream",
    )


def execute_script(
    image_path: str,
    output_directory: str,
    resolution_x: int,
    resolution_y: int,
    resolution_z: int,
    write_block_size: int,
    resume: bool,
) -> Iterator[str]:
    base_path = "/zjbs-data/share"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "convert_precomputed",
            "convert" "--write-block-size",
            str(write_block_size),
            "--resume" if resume else "--no-resume",
            "--base-url",
            "http://10.11.140.35:2000",
            "--base-path",
            os.path.join(base_path, image_path),
            os.path.join(base_path, output_directory),
            str(resolution_x),
            str(resolution_y),
            str(resolution_z),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="UTF-8",
        env={"PYTHONPATH": os.path.join(__file__, "..", "..")},
    )
    for line in process.stdout:
        yield f"data: {line}\n\n"

    code = process.wait()
    if code != 0:
        yield f"data: Failed, code: {code}\n\n"
    else:
        yield f"event: done\ndata: done\n\n"
