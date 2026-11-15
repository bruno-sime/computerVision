# T05 — MLP implementada do zero

Este trabalho implementa e avalia uma rede neural perceptron multicamadas (MLP) para classificar as três espécies do conjunto de dados Iris. A rede é construída no notebook, sem usar bibliotecas prontas de redes neurais para realizar o treinamento.

## O que foi implementado

- propagação direta vetorizada;
- função softmax na saída;
- entropia cruzada;
- backpropagation;
- inicialização Xavier ou He;
- treinamento com mini-batches;
- regularização L2;
- parada antecipada opcional;
- separação estratificada em treino, validação e teste;
- repetição das configurações com diferentes inicializações.

Além da implementação, o notebook compara configurações da rede e discute convergência, generalização e overfitting. A configuração regularizada escolhida obteve 96,67% de acurácia no conjunto de teste, com um erro entre `virginica` e `versicolor`.

## Como reproduzir

Abra [T05_MLP_from_scratch.ipynb](T05_MLP_from_scratch.ipynb) em Jupyter ou no VS Code e execute as células na ordem. O notebook contém a preparação dos dados, a implementação da MLP, os experimentos, os gráficos e a análise dos resultados.

O relatório em PDF e seus arquivos-fonte estão disponíveis na mesma pasta:

- `Relatorio_T05_MLP_from_scratch.pdf`;
- `Relatorio_T05_MLP_from_scratch.tex`;
- `Relatorio_T05_MLP_from_scratch.docx`.

Os resultados podem variar ligeiramente conforme a semente aleatória usada em uma nova execução.
