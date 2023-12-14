#!/usr/bin/env bash

source /env/bin/activate
uvicorn --host 0.0.0.0 --port 80 convert_precomputed_web.main:app
