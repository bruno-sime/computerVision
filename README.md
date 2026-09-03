# Segmentacao de imagem por textura

Este projeto implementa uma segmentacao classica, sem inteligencia artificial, para `image.jpg`.

O vetor de cada recorte tem 24 dimensoes: a media do modulo da resposta de 8 filtros em 3 escalas. Os filtros representam horizontal, vertical, 45 graus, 135 graus, Laplaciano, Laplaciano do Gaussiano, difusao e uma mascara circular. O agrupamento e feito por K-Means sobre a distancia euclidiana apos a padronizacao dos atributos.

## Execucao

```bash
python3 -m venv /tmp/computerVision-venv
/tmp/computerVision-venv/bin/python -m pip install -r requirements.txt
/tmp/computerVision-venv/bin/python segmentacao_textura.py --patches 32 --groups 4
```

Arquivos gerados em `resultados/`:

- `categorizacao_imagem.png`: grupos desenhados sobre a fotografia.
- `categorizacao_recortes.png`: grade dos recortes com seus grupos.
- `descritores_24d.csv`: tabela dos vetores e respectivos grupos.
- `descritores_24d.npy`: mesma matriz em formato NumPy.

Para usar mais recortes, por exemplo 64, execute `python segmentacao_textura.py --patches 64 --groups 4`.