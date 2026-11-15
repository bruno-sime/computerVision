"""Regera tabela e gráficos agregados a partir dos resultados distribuídos."""
import os,json
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/ru_matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1]
r=json.loads((P/'resultados/comparacao.json').read_text());s=json.loads((P/'resultados/resumo_candidatas.json').read_text())
lines=[]
for v in s:
 mean=f'{v["mean_span_min"]:.2f}'.replace('.',',');median=f'{v["median_span_min"]:.2f}'.replace('.',',')
 lines.append(' & '.join([v['config'],str(v['candidate_count']),str(v['complete_candidates']),mean,median])+' '+chr(92)*2)
(P/'artigo/tabela_candidatas.tex').write_text('\n'.join(lines)+'\n')
main=P/'artigo/main.tex'
text=main.read_text()
start=text.index('% BEGIN CANDIDATAS')
end=text.index('% END CANDIDATAS',start)
text=text[:start]+'% BEGIN CANDIDATAS'+chr(10)+chr(10).join(lines)+chr(10)+text[end:]
main.write_text(text)
fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
for v,label,col in zip(r,['A: x, 2 fps, 15 s','B: m, 2 fps, 15 s','C: x, 5 fps, 15 s','D: x, 2 fps, 5 s'],['#176582','#d18b24','#7061a4','#39836a']):
 ax.plot([11.25+i*.5 for i in range(6)],[v['faixas_30min'][str(i)]['deteccoes_medias'] for i in range(6)],marker='o',label=label,color=col)
ax.set(xlabel='Centro da faixa de meia hora',ylabel='Detecções rastreadas por imagem (média)',title='Saída dos quatro rastreadores no período completo')
ax.set_xticks([11.25+i*.5 for i in range(6)],['11:15','11:45','12:15','12:45','13:15','13:45']);ax.legend(fontsize=8);ax.grid(alpha=.2)
fig.text(.01,-.04,'Saídas do algoritmo: não são contagens reais de usuários nem medidas de permanência.',fontsize=9)
fig.savefig(P/'artigo/figuras/deteccoes_por_faixa.png',dpi=180,bbox_inches='tight');plt.close(fig)
print('Tabela e gráfico do artigo atualizados. Os parágrafos interpretativos requerem revisão se os resultados mudarem.')
