# T03 — Transformação perspectiva

Este trabalho retifica fotografias oblíquas do tabuleiro usado no T02. Os cantos internos são detectados automaticamente, os quatro extremos da grade são associados a uma vista frontal e uma homografia é aplicada com `cv2.warpPerspective`.

## Estrutura

```text
T03/
├── src/
│   ├── transform_perspective.py
│   └── build_report.py
├── results/
│   ├── annotated/
│   ├── comparisons/
│   └── rectified/
└── docs/
    ├── relatorio_artigo.md
    └── relatorio_artigo.pdf
```

As imagens de entrada não são duplicadas no T03. Por padrão, o programa lê `../T02/images/calibration`.

## Ambiente e execução

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run_all.sh
```

O script processa as imagens do T02 e recompila o relatório. Para processar uma imagem específica:

```bash
python src/transform_perspective.py \
  --input caminho/para/imagem.jpg \
  --output results
```

Opções úteis:

- `--cols 9 --rows 6`: quantidade de cantos internos;
- `--square-px 100`: resolução de saída por quadrado;
- `--calibration arquivo.npz`: corrige a distorção antes da retificação;
- `--limit N`: limita a quantidade de imagens processadas.

Como o tabuleiro possui 10 x 7 quadrados, a saída padrão tem 1000 x 700 pixels. A borda externa é mantida na vista retificada, embora a detecção use os 9 x 6 cantos internos.
