# T04 — Análise do conjunto Iris

Relatório sobre o conjunto de dados Iris, com análise exploratória, redução de dimensionalidade por PCA e classificação por K-NN. O relatório foi escrito em LaTeX, usando a base `abntex2` fornecida para a disciplina.

## Arquivos principais

- `main.tex`: fonte do relatório em LaTeX;
- `gerar_figuras.R`: script que gera os gráficos;
- `iris.csv`: dados utilizados na análise;
- `figuras/`: figuras incluídas no relatório;
- `T04_iris.Rmd`: versão complementar em R Markdown;
- `T04_iris.pdf` e `T04_iris.html`: versões renderizadas.

## Requisitos

É necessário ter R, os pacotes usados pelo script e uma instalação LaTeX disponível no sistema. As figuras podem ser recriadas com:

```bash
Rscript gerar_figuras.R
```

Depois, compile o relatório:

```bash
pdflatex main.tex
pdflatex main.tex
```

O relatório final é gerado a partir de `main.tex`. Os arquivos auxiliares da compilação podem ser removidos sem afetar os dados ou as figuras.
