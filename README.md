# Segmentacao de imagem por textura em C++

Implementacao classica, sem inteligencia artificial, para analisar `image.jpg`.

## O que o programa faz

1. Carrega a fotografia colorida e converte para tons de cinza.
2. Seleciona 32 recortes de `512x512` em uma grade regular.
3. Aplica oito filtros de textura: horizontal, vertical, 45 graus, 135 graus, Laplaciano, LoG, difusao e circular.
4. Processa cada filtro em tres escalas usando uma piramide Gaussiana (`1`, `1/2` e `1/4`), totalizando `8 x 3 = 24` atributos.
5. Calcula a media do modulo da resposta do filtro dentro de cada janela.
6. Padroniza os vetores e agrupa as regioes com K-Means, usando distancia euclidiana.
7. Gera uma imagem com a categorizacao sobre a fotografia e uma montagem dos recortes.

## Compilacao e execucao no macOS

O OpenCV deve estar instalado pelo Homebrew:

```bash
brew install opencv
cmake -S . -B build -G Ninja -DOpenCV_DIR="$(brew --prefix opencv)/lib/cmake/opencv4"
cmake --build build
./build/segmentacao_textura image.jpg resultados_cpp 32 4
```

Os argumentos sao, respectivamente, imagem de entrada, pasta de saida, quantidade de recortes e quantidade de grupos. O gerador Ninja e usado porque o `:` presente no caminho deste workspace causa conflito com regras do Make.

## Resultados

- `resultados_cpp/categorizacao_imagem.jpg`: grupos desenhados sobre a imagem original.
- `resultados_cpp/categorizacao_recortes.jpg`: recortes 512x512 em uma montagem com seus grupos.
- `resultados_cpp/descritores_24d.csv`: matriz dos vetores, coordenadas, nomes dos filtros e grupos.
- `resultados_cpp/descritores_24d.npy`: matriz 32x24 em formato NumPy para analise posterior.

O programa tambem imprime a compactacao final do K-Means, util para comparar execucoes com diferentes quantidades de grupos.