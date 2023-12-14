import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Iterator, Annotated

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from script_hub.task_queue import start_worker, stop_worker

CWD = Path(__file__).parent.parent.parent
SCRIPT_DIR = CWD / "scripts"

app = FastAPI()

app.mount("/web", StaticFiles(directory=CWD / "web"), name="web")


@app.on_event("startup")
def startup():
    start_worker()


@app.on_event("shutdown")
def shutdown():
    stop_worker()


@app.get("/")
def index():
    return RedirectResponse("/web/index.html")


BASE_PATH = PurePosixPath("/zjbs-data/share")


@app.get("/api/convert-simple-image")
def convert_simple_image(
    image_path: Annotated[str, Query()],
    output_directory: Annotated[str, Query()],
    resolution_x: Annotated[int, Query()],
    resolution_y: Annotated[int, Query()],
    resolution_z: Annotated[int, Query()],
    resume: Annotated[bool, Query()],
    write_block_size: Annotated[int, Query()] = 1024,
) -> StreamingResponse:
    cmd = [
        sys.executable,
        "-m",
        "convert_to_precomputed",
        "convert",
        "--base-url",
        "http://10.11.140.35:2000",
        "--base-path",
        str(BASE_PATH),
    ]
    if write_block_size is not None:
        cmd.append("--write-block-size")
        cmd.append(str(write_block_size))
    cmd.extend(
        [
            "--resume" if resume else "--no-resume",
            str(BASE_PATH / image_path.lstrip("/")),
            str(BASE_PATH / output_directory.lstrip("/")),
            str(resolution_x),
            str(resolution_y),
            str(resolution_z),
        ]
    )

    python_path = SCRIPT_DIR / "convert-simple-image"
    return response_stream(cmd, env={"PYTHONPATH": str(python_path)})


@app.get("/api/convert-labeled-image")
def convert_labeled_image(
    image: Annotated[str, Query()],
    output_directory: Annotated[str, Query()],
    resolution_x: Annotated[int, Query()] = 1,
    resolution_y: Annotated[int, Query()] = 1,
    resolution_z: Annotated[int, Query()] = 1,
    width: Annotated[int | None, Query()] = None,
    height: Annotated[int | None, Query()] = None,
) -> StreamingResponse:
    script_dir = SCRIPT_DIR / "convert-to-neuroglancer" / "python"
    cmd = [
        sys.executable,
        str(script_dir / "labeled_image_to_precomputed.py"),
        "-r",
        f"{resolution_x},{resolution_y},{resolution_z}",
        "-d",
        str(BASE_PATH / output_directory.lstrip("/")),
    ]
    if width is not None:
        cmd.append("-width")
        cmd.append(str(width))
    if height is not None:
        cmd.append("-height")
        cmd.append(str(height))
    cmd.append(str(BASE_PATH / image.lstrip("/")))

    return response_stream(cmd, env={"PYTHONPATH": str(script_dir)})


SCRIPTS = {
    "atlas-ellipsoid": "atlasEllipsoidAnnotation.mjs",
    "box": "boxAnnotations.mjs",
    "ellipsoid": "ellipsoidAnnotations.mjs",
    "line": "lineAnnotations.mjs",
    "sphere": "sphereAnnotations.mjs",
    "point": "pointAnnotation.mjs",
}


@app.get("/api/convert-annotation")
def convert_annotation(
    annotation_type: Annotated[str, Query()],
    output_directory: Annotated[str, Query()],
    resolution: Annotated[str, Query()],
    lower_bound: Annotated[str, Query()],
    upper_bound: Annotated[str, Query()],
    generate_index: Annotated[bool, Query()],
) -> StreamingResponse:
    script_dir = SCRIPT_DIR / "convert-to-neuroglancer" / "node"
    script = script_dir / SCRIPTS[annotation_type]
    cmd = [
        "node",
        str(script),
        f"--infoFile={BASE_PATH/output_directory.lstrip('/')}",
        f"--resolution={resolution}",
        f"--lowerBound={lower_bound}",
        f"--upperBound={upper_bound}",
        f"--targetDir={BASE_PATH/output_directory.lstrip('/')}",
        f"--generateIndex={generate_index}",
    ]
    return response_stream(cmd, cwd=script_dir)


def response_stream(cmd: list[str], **kwargs) -> StreamingResponse:
    return StreamingResponse(execute_script(cmd, **kwargs), media_type="text/event-stream")


def execute_script(cmd: list[str], **kwargs) -> Iterator[str]:
    logger.info(f"cmd={' '.join(cmd)}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **kwargs)
    for line in process.stdout:
        yield f"data: {line}\n"

    code = process.wait()
    yield f"event: done\ndata: Finished with return code: {code}\n\n"
