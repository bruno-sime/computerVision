# T02 — Calibração de câmera

Projeto de calibração monocular com OpenCV. O trabalho cobre a captura de imagens de um tabuleiro, a estimação dos parâmetros da câmera, a correção de distorção e a projeção de pontos 3D na imagem.

## Tabuleiro

- 9 x 6 cantos internos;
- 10 x 7 quadrados;
- quadrados de 25 mm x 25 mm;
- arquivo para impressão: `docs/checkerboard_A4_9x6_25mm.pdf`.

Imprima em tamanho real, sem usar a opção de ajustar à página, e confirme com uma régua se cada quadrado mede 25 mm.

## Ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Na primeira abertura da câmera, o macOS pode solicitar permissão em **Ajustes do Sistema > Privacidade e Segurança > Câmera**.

## Uso

Para descobrir o índice da câmera:

```bash
python src/capture_calibration.py --scan
```

Depois, capture as imagens variando a posição e a inclinação do tabuleiro:

```bash
python src/capture_calibration.py --camera 1 --count 30
```

Durante a captura, `SPACE` ou `c` salva uma imagem quando o tabuleiro é detectado, `r` remove as imagens da sessão, e `q` ou `ESC` encerra.

Com as imagens em `images/calibration/`, execute:

```bash
python src/calibrate.py
python src/undistort.py
python src/projection_experiment.py --limit 5
```

Ou rode o fluxo completo:

```bash
./run_all.sh
```

O experimento de projeção detecta o tabuleiro, calcula a pose com `solvePnP`, projeta um cubo de 50 mm e salva as coordenadas 3D, 2D e os erros de reprojeção.

## Resultados

Os arquivos principais ficam em `results/`:

- `calibration.npz` e `calibration.json`: parâmetros da câmera;
- `reprojection_errors.csv`: erro de reprojeção por imagem;
- `corners/`: detecção dos cantos;
- `undistorted/`: comparações antes e depois da correção;
- `projection/`: imagens e tabelas da projeção 3D.

O relatório e o modelo de relatório ficam em `docs/`.
