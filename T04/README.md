# T04 — relatório em LaTeX

O relatório usa a base `abntex2` adotada nos trabalhos da disciplina.

Arquivos principais:

- `main.tex`: relatório editável;
- `pacotes.sty`, `Macros.tex` e `UFPR.pdf`: arquivos da base LaTeX;
- `gerar_figuras.R`: reproduz os gráficos;
- `figuras/`: gráficos vetoriais usados no relatório;
- `iris.csv`: dados analisados;
- `T04_iris_LaTeX.pdf`: relatório final compilado.

Para reproduzir:

```sh
Rscript gerar_figuras.R
pdflatex main.tex
pdflatex main.tex
```
