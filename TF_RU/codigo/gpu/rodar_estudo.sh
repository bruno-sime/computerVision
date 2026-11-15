#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
video="${1:?Uso: bash rodar_estudo.sh /caminho/Video_1.mp4 [1 ou 2 processos]}"
parallel="${2:-2}"
[[ "$parallel" == 1 || "$parallel" == 2 ]] || { echo 'Use 1 ou 2 processos.'; exit 1; }
[[ -f "$video" ]] || { echo 'Vídeo não encontrado.'; exit 1; }
.venv/bin/python analisar_gpu.py doctor
# Baixar os pesos antes de iniciar os processos concorrentes.
.venv/bin/python - <<'PY'
from ultralytics import YOLO
for name in ['yolo11m-pose.pt','yolo11x-pose.pt']:
    YOLO(name)
PY
study="work/estudo_$(date +%Y%m%d_%H%M%S)_$$"
mkdir -p "$study"
cp analisar_gpu.py requirements.txt rodar_estudo.sh "$study/"
sha256sum "$video" > "$study/video_sha256.txt"
echo "$study" > ultimo_estudo.txt
echo "Saídas em: $study"
run_config() {
    local name="$1" model="$2" step="$3" gap="$4"
    .venv/bin/python analisar_gpu.py run --video "$video" --model "$model" \
      --imgsz 1280 --step "$step" --conf 0.15 --gap "$gap" \
      --output "$study/$name" > "$study/$name.log" 2>&1
}
failure=0
if [[ "$parallel" == 2 ]]; then
    run_config m_2fps_gap15 yolo11m-pose.pt 0.5 15 &
    first=$!
    run_config x_5fps_gap15 yolo11x-pose.pt 0.2 15 &
    second=$!
    wait "$first" || failure=1
    wait "$second" || failure=1
else
    run_config m_2fps_gap15 yolo11m-pose.pt 0.5 15 || failure=1
    run_config x_5fps_gap15 yolo11x-pose.pt 0.2 15 || failure=1
fi
# Este terceiro experimento começa depois dos dois primeiros.
run_config x_2fps_gap5 yolo11x-pose.pt 0.5 5 || failure=1
if [[ "$failure" != 0 ]]; then
    echo "Houve falha. Confira os logs em $study; não use execução incompleta."
    exit 1
fi
.venv/bin/python - "$study" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1])
for name in ['m_2fps_gap15','x_5fps_gap15','x_2fps_gap5']:
    assert json.loads((p/name/'conclusao.json').read_text())['completed'],name
print('As três novas execuções percorreram o arquivo inteiro.')
print('Comparar com a execução anterior: x, 2 fps, gap 15 s.')
print('Ainda é necessária a avaliação contra sessões sentadas anotadas.')
PY
archive="${study}.tar.gz"
tar -czf "$archive" -C "$(dirname "$study")" "$(basename "$study")"
echo "Resultados para enviar: $archive"
