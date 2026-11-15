# Verificações da entrega

- Conferência integral dos JSONL: número de observações, timestamps crescentes e coincidência com todas as linhas das tabelas de trajetórias.
- Cobertura concluída dos 107.981 quadros em cada condição e hash do vídeo idêntico entre Mac e servidor.
- Segmentação executada nas quatro condições; cores extraídas de quadros do vídeo selecionados pela mesma grade temporal nominal de cinco segundos, com timestamps do decodificador.
- Intervalos candidatos sem sobreposição no mesmo assento, dentro da duração do arquivo, com pelo menos 60 s; resumo numérico conferido contra cada CSV.
- Código Python publicado verificado sintaticamente; executores shell verificados com `bash -n`.
- PDF compilado com LaTeX e BibTeX, sem citações indefinidas nem caixas de texto excedentes; seis páginas renderizadas e inspecionadas visualmente após a última alteração.
- Autoria, professor, disciplina, link Git, referências, tabelas e figuras conferidos.

Limites: não há referência humana independente, teste temporal separado, precisão de identidade medida ou média validada de estudantes. Não foi realizada nova instalação/execução do pacote público no Ubuntu após esta organização; os resultados CUDA derivam dos arquivos efetivamente recebidos e auditados. Não houve publicação no GitHub.
