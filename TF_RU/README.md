# TF — permanência em assentos de um restaurante universitário

**Bruno Sime Ferreira Nunes** — Visão Computacional e Percepção — Prof. Eduardo Todt — UFPR, 2026.

Repositório de destino informado pelo autor: https://github.com/bruno-sime/computerVision

## Resultado e alcance

Estudo exploratório com quatro configurações de YOLO11-Pose/BoT-SORT durante toda a gravação das 11h às 14h. Implementa associação geométrica a quatro assentos e segmentação por disponibilidade e cor da roupa. A comparação, as referências assistidas e os exemplos de truncamento/fragmentação estão documentados no artigo.

**Não foi obtida uma média validada do tempo sentado dos estudantes.** As estatísticas de `candidatas_*.csv` descrevem intervalos produzidos por uma heurística, não sessões reais confirmadas. IDs não equivalem a pessoas. A checagem de 24 estados e os quatro contrastes temporais são referências visuais assistidas por modelo multimodal, não anotação humana independente nem teste separado. As referências de um minuto não descartam pausas menores que esse intervalo. Sua revisão pelo autor é recomendada antes da submissão.

## Organização

- `artigo/`: PDF de seis páginas, fonte LaTeX e figuras; adaptação do modelo Base UFPR fornecido ao formato de artigo.
- `codigo/gpu/`: execução da inferência e três experimentos adicionais; contém instruções próprias.
- `codigo/comparacao/`: auditoria completa de JSONL, tabelas e comparação de configurações.
- `codigo/sessoes/`: associação aos assentos, cor do torso, segmentação e checagens diagnósticas.
- `dataset/`: manifesto do vídeo, posições dos assentos, referências pontuais/temporais assistidas e série compacta de ocupação geométrica.
- `resultados/`: métricas, candidatos, configurações, versões e confirmações de conclusão.
- `testar_resultados.py`: checagens de integridade dos resultados distribuídos.

O pacote público contém dados tabulares e figuras agregadas, sem quadros identificáveis. O vídeo de 1,5 GB, as imagens de inspeção, os pesos e os JSONL completos não são distribuídos. O hash e as condições de acesso estão no manifesto. Isso documenta o conjunto de dados sem afirmar que o vídeo está publicamente disponível.

## Conferir a entrega sem o vídeo

Python 3 padrão é suficiente:

```bash
python3 testar_resultados.py
```

As quatro condições são A: x/2 fps/15 s; B: m/2 fps/15 s; C: x/5 fps/15 s; D: x/2 fps/5 s. Entrada 1280, FP16, confiança 0,15, IoU 0,60, BoT-SORT sem ReID. Todos os 107.981 quadros foram percorridos. B e C rodaram simultaneamente; tempos de execução não são benchmark controlado.

## Reproduzir as inferências no Ubuntu/CUDA

Use o Python com PyTorch/CUDA instalado. Em `codigo/gpu`, siga o setup e os comandos do README. Para reproduzir a referência A:

```bash
bash run.sh --video /caminho/Video_1.mp4 --model yolo11x-pose.pt --imgsz 1280 --step 0.5 --conf 0.15 --gap 15 --output work/x_integral_v1
```

Para as demais condições:

```bash
bash rodar_estudo.sh /caminho/Video_1.mp4 2
```

O número 2 permite dois processos simultâneos. Cada execução usa pasta nova; estado do rastreador não é retomado após interrupção. A disponibilidade de memória deve ser conferida na máquina. A geração dos candidatos é exploratória e não foi calibrada contra teste independente. A versão Ultralytics foi fixada em 8.4.214; as versões efetivamente usadas estão em `resultados/configuracoes/`.

## Reproduzir a análise a partir dos arquivos completos

Dependências de análise: Python, NumPy, OpenCV, Matplotlib e FFmpeg. Pode-se usar o ambiente da inferência. Na raiz desta pasta:

```bash
RU_PYTHON=/caminho/ambiente/bin/python bash reproduzir_analise.sh \
  /caminho/Video_1.mp4 \
  /caminho/work/x_integral_v1 \
  /caminho/work/estudo_20261115_202015_2136803
```

O programa usa o vídeo para extrair cores do torso e exige os JSONL integrais das quatro condições. Os caminhos específicos da máquina original nos arquivos de configuração são registros de proveniência. Os scripts publicados recebem caminhos pelas variáveis `RU_VIDEO`, `RU_BASELINE` e `RU_ESTUDO`, configuradas pelo executor. O pós-processamento usa uma grade de 5 s comum aos quatro métodos; não preserva toda a resolução de 5 fps de C.

As caches `codigo/sessoes/assentos_*.json` e `cores.json` devem ser removidas **pelo usuário**, se mudar vídeo, regiões ou configuração, antes de recomputar. São arquivos derivados e estão ignorados no Git. As regiões e as referências desta entrega foram definidas para este enquadramento, não para qualquer câmera.

## Compilar o artigo

Requer TeX Live com abnTeX2 e os pacotes da base UFPR:

```bash
cd artigo
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

O PDF distribuído chama-se `TF_RU_Bruno_Sime.pdf`; a recompilação gera `main.pdf`.

## Publicação no Git

Coloque esta pasta `TF_RU` dentro do repositório existente, preservando os demais trabalhos. O link do artigo aponta para a raiz desse repositório. Este pacote foi preparado localmente: seu conteúdo ainda precisa ser enviado ao GitHub pelo autor. Não foram criados commits nem enviada alteração ao serviço.

## Limitações e continuação

A amostra espacial é de conveniência e envolve apenas uma câmera e um almoço. Não há generalização demonstrada para o RU inteiro ou outros dias. Ausência de detecção não prova saída; roupas semelhantes podem unir ocupantes; alterações de pose podem dividir uma permanência. Para obter uma média de estudantes defensável, falta uma referência temporal independente, separação calibração/teste e validação dos eventos e das pausas. O artigo relata esse limite como resultado experimental, sem inventar precisão ou duração real.
