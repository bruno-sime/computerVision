# Trabalho final — Permanência sentado no RU

Estudo de viabilidade para estimar o tempo de permanência sentado no restaurante universitário a partir de vídeo. O pacote reúne o código de rastreamento, os dados derivados, os resultados, o artigo e os arquivos usados para conferir a reprodução da análise.

## Escopo e limites

O objetivo é acompanhar trajetórias e organizar candidatos para revisão humana. A detecção de uma pessoa e a manutenção de um ID não provam, sozinhas, que ela permaneceu sentada durante todo o intervalo. Por isso, os tempos só entram em uma média depois de confirmar no vídeo o início, o fim, as pausas e eventuais trocas de pessoa.

O material não contém o vídeo bruto nem imagens identificáveis. Também não apresenta uma média validada de tempo sentado dos estudantes. As limitações, os intervalos incompletos e as condições analisadas estão descritos no artigo.

## Organização

- `codigo/`: scripts de análise, comparação, sessões e execução com GPU;
- `dataset/`: metadados e tabelas derivadas;
- `resultados/`: saídas das execuções e tabelas para revisão;
- `artigo/`: artigo final e arquivos LaTeX;
- `reproduzir_analise.sh`: roteiro de reprodução;
- `testar_resultados.py`: verificações dos arquivos gerados;
- `MANIFEST_SHA256.txt`: hashes dos arquivos da entrega;
- `VERIFICACOES.md`: conferências realizadas e limitações conhecidas.

## Reprodução

As execuções completas foram preparadas para um Ubuntu com GPU NVIDIA e PyTorch com CUDA. Consulte as instruções específicas em [ENTREGA.md](ENTREGA.md) e nos READMEs dentro de `codigo/`.

Depois de conferir os arquivos, execute as verificações:

```bash
bash -n reproduzir_analise.sh
python testar_resultados.py
```

O artigo final está em [artigo/TF_RU_Bruno_Sime.pdf](artigo/TF_RU_Bruno_Sime.pdf).
