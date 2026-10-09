# Calibracao de camera com OpenCV

Projeto para calibracao monocular, remocao de distorcao e experimento de projecao de pontos 3D para coordenadas 2D.

## Padrao utilizado

- Tabuleiro: **9 x 6 cantos internos**
- Portanto: **10 x 7 quadrados**
- Tamanho de cada quadrado: **25 mm x 25 mm**
- Arquivo para impressao: `docs/checkerboard_A4_9x6_25mm.pdf`
- Papel: A4 horizontal
- Impressao: **100% / Tamanho real / Actual size**. Nao usar "Ajustar a pagina".

Depois de imprimir, meca um quadrado com uma regua. Ele deve ter exatamente 25 mm. Para maior rigidez, cole a folha em papelao/foam board sem deformar o papel.

## 1. Ambiente no macOS

No Terminal, dentro desta pasta:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Na primeira abertura da camera, o macOS pode pedir permissao. Se necessario, habilite Terminal/iTerm/Python em:

`Ajustes do Sistema > Privacidade e Seguranca > Camera`

## 2. Descobrir o indice da Logitech

```bash
python src/capture_calibration.py --scan
```

Se a camera interna for indice 0, a Logitech frequentemente aparece como 1, mas use o indice que funcionar no seu Mac.

## 3. Capturar 30 fotos

Exemplo com Logitech no indice 1:

```bash
python src/capture_calibration.py --camera 1 --count 30
```

Controles:

- `SPACE` ou `c`: salva quando o tabuleiro foi detectado;
- `f`: salva mesmo sem deteccao (nao recomendado);
- `r`: apaga as imagens capturadas nesta sessao;
- `q` ou `ESC`: encerra.

### Como tirar boas fotos

Varie bastante a pose. Nao tire 30 imagens quase iguais. Inclua:

- tabuleiro no centro;
- perto dos quatro cantos da imagem;
- inclinado para esquerda/direita;
- inclinado para cima/baixo;
- algumas imagens proximas;
- algumas mais distantes;
- sempre com o tabuleiro inteiro e nitido.

Evite reflexos, movimento e desfoque. Mantenha a mesma resolucao durante toda a calibracao.

## 4. Calibrar

```bash
python src/calibrate.py
```

Saidas principais:

- `results/calibration.npz`: parametros para os scripts;
- `results/calibration.json`: matriz K e coeficientes de distorcao em formato legivel;
- `results/reprojection_errors.csv`: erro por imagem;
- `results/corners/`: imagens com os cantos detectados.

A matriz intrinseca possui a forma:

```text
K = [ fx   0  cx ]
    [  0  fy  cy ]
    [  0   0   1 ]
```

## 5. Corrigir a distorcao

```bash
python src/undistort.py
```

As comparacoes `original | corrigida` ficam em `results/undistorted/`.

Para testar apenas uma imagem:

```bash
python src/undistort.py --input images/calibration/calib_EXEMPLO.jpg
```

## 6. Experimento 3D -> 2D

```bash
python src/projection_experiment.py --limit 5
```

O script:

1. detecta o tabuleiro;
2. calcula a pose com `solvePnP`;
3. define um cubo 3D de 50 mm;
4. projeta seus vertices usando `projectPoints`;
5. desenha cubo e eixos XYZ na imagem;
6. salva as coordenadas 3D e 2D em CSV;
7. compara pontos conhecidos do tabuleiro com seus pontos reprojetados.

Resultados em `results/projection/`.

Arquivos `*_projected_points.csv` possuem colunas:

```text
point, X_mm, Y_mm, Z_mm, u_px, v_px
```

Arquivos `*_verification.csv` mostram a comparacao entre o ponto detectado na imagem e o ponto calculado pelo modelo, incluindo o erro em pixels.

## 7. Rodar tudo depois das fotos

```bash
./run_all.sh
```

## 8. O que colocar no relatorio

Use `docs/relatorio_modelo.docx` e substitua os campos destacados/entre colchetes pelos valores obtidos no seu experimento.

Inclua principalmente:

- modelo da camera Logitech utilizada;
- resolucao de captura;
- dimensoes do tabuleiro;
- quantidade de imagens obtidas e quantidade efetivamente usada;
- matriz intrinseca K;
- coeficientes de distorcao;
- erro de reprojecao;
- figuras antes/depois da correcao de distorcao;
- pelo menos 3 imagens do cubo 3D projetado;
- tabela com algumas coordenadas 3D, coordenadas 2D e erros;
- conclusao;
- link do repositorio Git.

## Estrutura

```text
camera_calibration_project/
├── README.md
├── requirements.txt
├── run_all.sh
├── src/
│   ├── capture_calibration.py
│   ├── calibrate.py
│   ├── undistort.py
│   └── projection_experiment.py
├── images/
│   └── calibration/
├── results/
│   ├── corners/
│   ├── undistorted/
│   └── projection/
└── docs/
    ├── checkerboard_A4_9x6_25mm.pdf
    └── relatorio_modelo.docx
```

## Relatório no padrão UFPR

O relatório LaTeX baseado na base UFPR fornecida está em `docs/relatorio_ufpr/`.
O arquivo `relatorio_preliminar.pdf` permite visualizar a versão atual. Campos marcados como `[PREENCHER: ...]` serão substituídos pelos resultados reais após a calibração.
