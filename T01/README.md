# T01 — Segmentação por textura

Este trabalho segmenta uma fotografia de uma placa eletrônica usando descritores de textura e K-Means. A implementação principal está em C++17 com OpenCV e não usa modelos de aprendizado profundo.

## Método

1. A imagem é convertida para tons de cinza.
2. São selecionados 32 recortes de `512 x 512` pixels.
3. Cada recorte é processado com oito filtros: horizontal, vertical, diagonais de 45° e 135°, Laplaciano, LoG, difusão e circular.
4. Os filtros são aplicados em três escalas de uma pirâmide Gaussiana.
5. A média do módulo das respostas forma um vetor de 24 atributos por recorte.
6. Os vetores são padronizados e agrupados com K-Means.

O resultado mostra os grupos sobre a imagem original e organiza os recortes em uma montagem para facilitar a comparação visual.

## Dependências

No macOS, instale o OpenCV e o Ninja:

```bash
brew install opencv ninja
```

## Compilação e execução

Dentro desta pasta:

```bash
cmake -S . -B build -G Ninja \
  -DOpenCV_DIR="$(brew --prefix opencv)/lib/cmake/opencv4"
cmake --build build
./build/segmentacao_textura image.jpg resultados_cpp 32 4
```

Os quatro argumentos do programa são, nesta ordem: imagem de entrada, pasta de saída, quantidade de recortes e quantidade de grupos. O Ninja evita problemas com o caractere `:` presente no caminho do workspace.

Também há uma implementação em Python em `segmentacao_textura.py`, usada para comparação e geração dos resultados da pasta `resultados/`.

## Saídas

- `categorizacao_imagem.jpg`: grupos desenhados sobre a imagem original;
- `categorizacao_recortes.jpg`: montagem dos recortes e seus grupos;
- `descritores_24d.csv`: descritores, coordenadas, filtros e grupos;
- `descritores_24d.npy`: matriz `32 x 24` em formato NumPy.

O relatório completo está em [RELATORIO.md](RELATORIO.md).
