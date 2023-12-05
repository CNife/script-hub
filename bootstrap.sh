#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=/home/cnife/code/convert_precomputed_web/src
conda activate convert-precomputed-web

uvicorn convert_precomputed_web.main:app --host 0.0.0.0 --port 6000
