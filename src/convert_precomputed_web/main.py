import os.path
from pathlib import Path
import subprocess
import sys
from typing import Iterator, Annotated

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, StreamingResponse

CWD: Path = Path(__file__).parent.parent.parent

app = FastAPI()


@app.get("/")
def index():
    return FileResponse(CWD / "web" / "index.html")


@app.get("/run")
def run(
    image_path: Annotated[str, Query(alias="imagePath")],
    output_directory: Annotated[str, Query(alias="outputDirectory")],
    resolution_x: Annotated[int, Query(alias="resolutionX")],
    resolution_y: Annotated[int, Query(alias="resolutionY")],
    resolution_z: Annotated[int, Query(alias="resolutionZ")],
    resume: Annotated[bool, Query(alias="resume")],
    write_block_size: Annotated[int, Query(alias="writeBlockSize")] = 1024,
):
    return StreamingResponse(
        execute_script(
            image_path,
            output_directory,
            resolution_x,
            resolution_y,
            resolution_z,
            write_block_size,
            resume,
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
    cmd = [
        sys.executable,
        "-m",
        "convert_to_precomputed",
        "convert",
        "--base-url",
        "http://10.11.140.35:2000",
        "--base-path",
        base_path,
    ]
    if write_block_size is not None:
        cmd.append("--write-block-size")
        cmd.append(str(write_block_size))
    cmd.extend(
        [
            "--resume" if resume else "--no-resume",
            os.path.join(base_path, image_path.lstrip("/")),
            os.path.join(base_path, output_directory.lstrip("/")),
            str(resolution_x),
            str(resolution_y),
            str(resolution_z),
        ]
    )
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="UTF-8",
        env={"PYTHONPATH": str(CWD / "src")},
    )
    for line in process.stdout:
        yield f"data: {line}\n\n"

    code = process.wait()
    if code != 0:
        yield f"data: Failed, code: {code}\n\n"
    else:
        yield f"event: done\ndata: done\n\n"
