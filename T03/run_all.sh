#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

python3 src/transform_perspective.py \
  --input ../T02/images/calibration \
  --calibration ../T02/results/calibration.npz \
  --output results

python3 src/build_report.py \
  --summary results/summary.json \
  --output docs/relatorio_artigo.pdf

echo "Concluido: resultados em T03/results e relatorio em T03/docs/relatorio_artigo.pdf"

