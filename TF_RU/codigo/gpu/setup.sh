#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ru_source_sites="$("${PYTHON:-python3}" -c 'import site; print("\n".join(site.getsitepackages()))')"
"${PYTHON:-python3}" -m venv --system-site-packages .venv
.venv/bin/python -c 'import pathlib,sys,sysconfig; pathlib.Path(sysconfig.get_paths()["purelib"],"source_pytorch_environment.pth").write_text(sys.argv[1]+"\n")' "$ru_source_sites"
PIP_USER=0 .venv/bin/python -m pip install --ignore-installed --no-deps --only-binary=:all: 'numpy>=1.26,<3'
PIP_USER=0 .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python analisar_gpu.py doctor

