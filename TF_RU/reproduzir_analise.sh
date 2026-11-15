#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
[[ $# -eq 3 ]] || { echo 'Uso: bash reproduzir_analise.sh VIDEO.mp4 PASTA_BASELINE PASTA_ESTUDO'; exit 1; }
export RU_VIDEO="$(realpath "$1")"
export RU_BASELINE="$(realpath "$2")"
export RU_ESTUDO="$(realpath "$3")"
ru_python="${RU_PYTHON:-python3}"
"$ru_python" codigo/comparacao/comparar.py
"$ru_python" codigo/sessoes/extrair_assentos.py
"$ru_python" codigo/sessoes/segmentar.py
"$ru_python" codigo/sessoes/verificar_referencias.py
"$ru_python" codigo/sessoes/gerar_figuras.py
cp codigo/comparacao/comparacao.csv codigo/comparacao/comparacao.json codigo/comparacao/integridade_video.json resultados/
cp codigo/sessoes/candidatas_*.csv codigo/sessoes/contraste_temporal_*.json codigo/sessoes/resumo_candidatas.json codigo/sessoes/checagem_pontual.json resultados/
"$ru_python" codigo/atualizar_artigo.py
"$ru_python" testar_resultados.py
