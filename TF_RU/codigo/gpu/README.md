# Permanência sentado no RU — período completo, 11h às 14h

Destino: Ubuntu com NVIDIA RTX 6000 Ada de 48 GB e PyTorch com CUDA já instalado.
Este pacote prepara rastreamento e evidências para conferir as sessões. **Ainda não é um medidor validado e totalmente automático de tempo sentado.**

## Escopo

- Percorrer toda a gravação, aproximadamente 2 h 59 min 58 s, sem limitar o estudo ao piloto.
- Horário de referência informado: 11h–14h. O arquivo termina aproximadamente às 13:59:58.
- Usar o campo visível da câmera. A abrangência temporal de três horas não implica observar todos os assentos ou todas as pessoas do RU.
- Medir tempo efetivamente sentado: fim menos início, descontando pausas em pé. Registrar sessões incompletas e casos encobertos separadamente.
- Produzir média e mediana globais e por faixa de início de 30 minutos, apenas após confirmar as sessões.

## Executar no Ubuntu

Transfira esta pasta e o vídeo para o servidor. O vídeo deve ser a gravação integral; não é necessário transferir o trecho piloto. O pacote não acessa o servidor automaticamente.

Ative o ambiente que já possui PyTorch/CUDA e execute:

```bash
bash setup.sh
bash run.sh --video /caminho/Video_1.mp4
```

Para manter a execução após desconectar:

```bash
nohup bash run.sh --video /caminho/Video_1.mp4 > execucao.log 2>&1 &
```

Se o interpretador com CUDA se chama `python`, configure antes de executar o setup:

```bash
PYTHON="$(command -v python)" bash setup.sh
```

O setup cria um ambiente separado e reutiliza o PyTorch existente. A primeira execução pode baixar os pesos públicos do modelo. O vídeo é processado localmente no servidor.

## Configuração inicial

- YOLO11x-pose, resolução de entrada 1280, CUDA e precisão FP16.
- BoT-SORT, câmera fixa, associação por movimento; aparência/ReID desativada nesta primeira configuração.
- Uma observação a cada 0,5 segundo, aproximadamente 21.600 observações ao longo de três horas. O arquivo é percorrido integralmente. Os tempos são lidos do vídeo, não inferidos apenas pelo índice de quadro.
- Tolerância inicial de 15 segundos para manter trajetórias perdidas. **Essa tolerância não autoriza preencher 15 segundos como tempo sentado.**
- Modelo e parâmetros são hipóteses iniciais a validar; a memória da GPU não garante detecções corretas nem um prazo de execução.

Para outra configuração, use uma pasta de saída nova:

```bash
bash run.sh --video /caminho/Video_1.mp4 --model yolo11m-pose.pt --output work/comparacao_m
```

O programa preserva pastas que já contêm observações. Não retoma estado do rastreador após interrupção; uma nova execução deve usar outra pasta.

## Resultados

Em `work/integral/`:

- `observacoes.jsonl`: caixas, pontos corporais, IDs temporários e timestamps.
- `trechos_para_revisao.csv`: intervalos em que cada ID apareceu. **Não são tempos sentados.**
- `revisao/`: imagens anotadas a cada 15 minutos.
- `config.json`, `versoes.txt`, `tracker.yaml`: configuração reproduzível.
- `conclusao.json`: conclusão do percurso e conferência da contagem de quadros. Verifique `completed` antes de usar os dados.
- `sessoes_validadas_MODELO.csv`: tabela para registrar sessões conferidas no vídeo.

## Obter uma média defensável

Detectar uma pessoa e manter um ID não demonstra que ela permaneceu sentada durante todo o intervalo. A revisão deve confirmar o ato de sentar, o de levantar, as pausas e possíveis trocas de pessoa no mesmo assento. O rastreamento acelera a busca por esses eventos; não os valida sozinho.

Preencha a tabela com segundos relativos a 11h. Use `validada=1` somente após conferência; os campos de incompletude usam 0/1. `pausas_em_pe_s` deve ser preenchido, inclusive com zero quando não houve pausa. Não preencha tempos ocultos por suposição. Renomeie a tabela para `sessoes_validadas.csv` e execute:

```bash
.venv/bin/python analisar_gpu.py resumir --csv work/integral/sessoes_validadas.csv
```

O resumo mantém incompletas e não validadas fora da média e informa suas quantidades. A média das sessões completas pode ter viés; não representa automaticamente as pessoas encobertas nem o restaurante inteiro. Separar faixas pelo início da sessão também exige atenção ao fim da gravação.

Para um resultado automático definitivo, falta validar a associação pessoa–assento e a classificação sentado/em pé com anotações distribuídas pelo período, incluindo horários cheios. Reportar erro de duração em minutos, falhas de associação, cobertura e exclusões; não apenas exemplos que funcionaram.

## Situação dos testes

A primeira passagem local utilizou YOLO11m-pose, uma observação a cada cinco segundos, e concluiu 2.160 observações distribuídas por toda a duração. A versão Ultralytics está fixada na versão local verificada, 8.4.214. A interface de rastreamento BoT-SORT e a leitura de timestamps foram verificadas em seis observações sequenciais do início do arquivo. A execução CUDA do modelo x precisa ser verificada nessa máquina Ubuntu. Não foi feita conexão ao servidor nem calculada uma média de permanência a partir de IDs brutos.

Referências: [rastreamento Ultralytics](https://docs.ultralytics.com/modes/track/), [estimação de pose](https://docs.ultralytics.com/tasks/pose/).
