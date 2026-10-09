#!/usr/bin/env bash
set -euo pipefail
python3 src/calibrate.py
python3 src/undistort.py
python3 src/projection_experiment.py
