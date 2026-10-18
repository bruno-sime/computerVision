# T03 - Transformacao perspectiva com OpenCV

Aplicacao simples que transforma fotografias obliquas do tabuleiro usado no T02 em vistas aereas retificadas. O programa detecta automaticamente os 9 x 6 cantos internos do tabuleiro, estima uma homografia e aplica `cv2.warpPerspective`.

Repositorio: <https://github.com/bruno-sime/computerVision/tree/main/T03>

## Estrutura

```text
T03/
├── README.md
├── requirements.txt
├── run_all.sh
├── src/
│   ├── transform_perspective.py
│   └── build_report.py
├── results/
│   ├── annotated/
│   ├── comparisons/
│   ├── rectified/
│   └── summary.json
└── docs/
    ├── relatorio_artigo.md
    └── relatorio_artigo.pdf
```

As fotografias não são duplicadas: a entrada padrão é `../T02/images/calibration`.

## Execucao

No terminal, dentro de `T03`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run_all.sh
```

O comando processa todas as imagens do T02 e recompila o relatório PDF. Para processar uma imagem ou outra pasta:

```bash
python3 src/transform_perspective.py --input caminho/para/imagem.jpg --output results
```

Argumentos úteis:

- `--cols 9 --rows 6`: número de cantos internos do tabuleiro;
- `--square-px 100`: resolução de saída por quadrado;
- `--calibration arquivo.npz`: corrige primeiro a distorção da lente (opcional);
- `--limit N`: limita o número de imagens, útil para testes rápidos.

## Metodo

Os quatro cantos extremos da grade detectada são associados a quatro posições conhecidas em uma vista frontal. A matriz de homografia `H` satisfaz, em coordenadas homogêneas,

```text
s [u v 1]^T = H [x y 1]^T
```

Como o padrão possui 10 x 7 quadrados, a saída padrão tem 1000 x 700 pixels. Os cantos internos são colocados com uma margem de um quadrado, preservando também a borda externa do tabuleiro.

