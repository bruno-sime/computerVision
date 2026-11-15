# Roteiro de estudo — pitch de 5 minutos, com a média

Bruno Sime Ferreira Nunes · Visão Computacional e Percepção · Prof. Eduardo Todt

**Resultado central: média nominal de 16 min 16 s em cinco sessões completas do assento S2, revisadas visualmente por IA. Uma sessão censurada ficou fora do cálculo.** Os tempos são metas de ensaio.

## Slide 1 — Permanência à mesa no RU

**0:00 a 0:25 (25 s)**

Meu projeto investiga se uma câmera de segurança consegue estimar quanto tempo uma pessoa permanece sentada à mesa no restaurante universitário. A proposta usa uma gravação real de almoço e compara configurações de visão computacional. O foco da apresentação é mostrar o método, os experimentos e até onde os resultados permitem chegar.

## Slide 2 — Uma gravação de todo o almoço

**0:25 a 1:00 (35 s)**

A análise cobre o período informado das onze às quatorze horas, em uma gravação de quase três horas. As quatro configurações percorreram todos os cento e sete mil novecentos e oitenta e um quadros. A etapa automática considera quatro regiões de assento. A revisão temporal aprofundada concentra-se no assento S2, escolhido por visibilidade e acompanhado durante o arquivo inteiro. Essa distinção é essencial: a cobertura do horário é completa, mas a média descreve uma amostra de um assento, sem representar todos os frequentadores do RU.

## Slide 3 — Da detecção aos episódios candidatos

**1:00 a 1:45 (45 s)**

O YOLO11-Pose detecta pessoas e estima pontos corporais. O BoT-SORT associa as detecções ao longo do vídeo e atribui identificadores temporários. Uma regra geométrica aproxima o quadril das regiões dos assentos. O pós-processamento usa detecções e cor da roupa para propor episódios. Para calcular a média apresentada, uma revisão visual por IA conferiu as sessões do assento S2: a triagem utilizou quadros de um minuto, o interior dos episódios passou por conferência a cada dez segundos e as transições de sentar e levantar receberam refinamento em quadros de dois segundos. Essa revisão não constitui validação humana independente.

## Slide 4 — Quatro configurações comparáveis

**1:45 a 2:25 (40 s)**

Usei como referência o modelo grande, com duas observações por segundo e quinze segundos de tolerância a perdas. Nas demais configurações, alterei uma variável por vez: o tamanho do modelo, a frequência de observação ou a tolerância. Mantive a resolução de entrada e os demais parâmetros. As inferências rodaram na RTX 6000 Ada de quarenta e oito gigabytes. Duas execuções compartilharam a GPU, então seus tempos não permitem uma comparação isolada de velocidade entre os modelos.

## Slide 5 — O rastreamento variou entre as configurações

**2:25 a 3:15 (50 s)**

A referência gerou quatro mil duzentos e oitenta IDs. O modelo médio gerou quatro mil oitocentos e oitenta e três. Com cinco observações por segundo, o modelo grande gerou sete mil duzentos e três. Reduzindo a tolerância para cinco segundos, apareceram cinco mil seiscentos e setenta e sete. O ponto importante é interpretar o significado desses números. Eles contam identificadores emitidos pelo rastreador. Uma mesma pessoa pode receber vários IDs, e uma associação incorreta pode unir pessoas diferentes. Portanto, mais IDs ou menos IDs, isoladamente, não definem uma configuração vencedora nem o número de estudantes.

## Slide 6 — A média das sessões revisadas

**3:15 a 4:15 (60 s)**

A revisão visual identificou cinco sessões completas no assento S2. As durações nominais foram quatorze minutos e dez segundos, cinco minutos e quarenta e quatro segundos, vinte e cinco minutos e dois segundos, vinte e dois minutos e cinquenta e quatro segundos e treze minutos e trinta segundos. A soma é de quatro mil oitocentos e oitenta segundos. Dividindo por cinco, a média é de dezesseis minutos e dezesseis segundos. A mediana é de quatorze minutos e dez segundos. Uma sexta sessão continua em andamento quando o vídeo termina, por isso ficou fora da média de completas. Os horários são estimativas por pontos médios. Pausas breves entre as imagens podem passar despercebidas, e não houve validação humana independente.

## Slide 7 — Conclusão e alcance da média

**4:15 a 5:00 (45 s)**

O projeto entrega uma média descritiva da amostra: dezesseis minutos e dezesseis segundos, a partir de cinco sessões completas de um único assento. A contribuição combina processamento reproduzível, comparação de quatro configurações e revisão temporal auditável. A média deriva da revisão visual por IA, e não da duração dos IDs. O resultado não representa todo o restaurante e ainda precisa de validação humana independente para uso operacional. A continuidade do ocupante, as oclusões e a sessão incompleta são limitações explícitas. O próximo passo é ampliar os assentos e os dias observados e avaliar os eventos contra uma referência independente.

## Perguntas prováveis

**Qual foi a média?**
16 min 16 s, calculada como 4.880 segundos divididos por cinco sessões completas. A mediana é 14 min 10 s.

**Essa é a média dos estudantes do RU inteiro?**
Não. É a média nominal da amostra de um único assento, em um almoço, com revisão visual por IA. A imagem não confirma quem é estudante.

**Por que excluiu uma sessão?**
O ocupante ainda estava sentado quando a gravação terminou. O tempo total é desconhecido. Seu trecho observado tinha pelo menos 18 min 02 s. Incluí-lo como completo distorceria o cálculo. A exclusão também limita a representatividade da média.

**Quem fez a revisão?**
O assistente de IA realizou a conferência visual. O artigo não atribui uma revisão humana ao autor e não a apresenta como validação humana independente.

**Como os tempos foram medidos?**
Triagem em quadros de 60 s, conferência interna em 10 s e refinamento dos limites em quadros de 2 s. Cada evento fica em um intervalo. O cálculo usa seus pontos médios.

**Qual é a incerteza?**
Os limites dos eventos permitem médias de aproximadamente 16 min 11 s a 16 min 21 s apenas pela quantização. Isso não é intervalo de confiança e não inclui erro de interpretação, oclusões ou pausas breves entre imagens.

**O algoritmo automático também chegou a essa média?**
Não. A média principal vem das sessões revisadas. Os candidatos automáticos sofrem fragmentação e não são substitutos diretos dos tempos revisados.

**Por que a GPU de 48 GB não resolveu tudo?**
A GPU acelera a inferência. Oclusões, associação do ocupante à cadeira e validação temporal são problemas de observação e método.

**Qual configuração venceu?**
Não declaramos uma vencedora. Contar mais ou menos IDs não demonstra precisão. Falta teste independente de identidade e duração.

**Os arquivos já estão no GitHub?**
Confirme o envio da pasta de entrega antes da apresentação. O pacote foi preparado localmente e o artigo aponta para o repositório informado.

## Ensaio

1. Leia em voz alta e explique a conta da média sem consultar o texto.
2. Confira os marcos: slide 3 em 1:00, slide 5 em 2:25 e conclusão em 4:15.
3. Se passar de cinco minutos, resuma a leitura dos quatro totais de IDs. Preserve a média, o tamanho da amostra e suas limitações.
4. Memorize a frase central: “A média nominal da amostra foi de 16 minutos e 16 segundos em cinco sessões completas de um assento, com revisão visual por IA.”

## Apoio visual durante o ensaio

No slide 2, aponte a região amarela do enquadramento. No slide 6, use os recortes para mostrar a diferença entre sentado e em pé; os horários são exemplos da sessão E2. Mantenha os tempos de fala indicados acima.
