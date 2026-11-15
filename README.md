# Visão Computacional

Repositório com os trabalhos desenvolvidos na disciplina de Visão Computacional e Percepção, da Universidade Federal do Paraná.

Os projetos foram feitos em Python, C++ e R, de acordo com o método utilizado em cada atividade. Cada pasta possui seu próprio código, arquivos de entrada, resultados e instruções de execução.

## Trabalhos

| Pasta | Tema |
|---|---|
| [T01](T01/) | Segmentação de imagem por textura usando filtros clássicos e K-Means |
| [T02](T02/) | Calibração de câmera, correção de distorção e projeção 3D |
| [T03](T03/) | Transformação perspectiva e retificação de imagens |
| [T04](T04/) | Análise do conjunto Iris com PCA e K-NN |
| [T05](T05/) | Classificação das espécies de Iris com uma MLP implementada do zero |
| [TF_RU](TF_RU/) | Estudo de viabilidade para estimar permanência sentado no restaurante universitário |

## Organização

Os trabalhos são independentes, mas alguns aproveitam arquivos gerados em etapas anteriores. O T03, por exemplo, usa como entrada padrão as imagens de calibração do [T02](T02/).

Em geral, os resultados prontos ficam na pasta `results/` ou `resultados/` de cada trabalho. Relatórios, figuras e materiais de apoio ficam em `docs/`, quando essa pasta existe.

## Ambiente

Os comandos de instalação e execução estão nos READMEs de cada trabalho. Como regra geral:

- os projetos Python usam um ambiente virtual próprio e o arquivo `requirements.txt`;
- o T01 depende do OpenCV instalado no sistema e usa CMake;
- o T04 depende de R e de uma instalação LaTeX;
- o T05 é executado a partir do notebook Jupyter;
- o TF_RU possui instruções próprias para análise e conferência dos resultados.

## Autor

Bruno Sime Ferreira Nunes  
GRR20190568

Universidade Federal do Paraná — Visão Computacional e Percepção
