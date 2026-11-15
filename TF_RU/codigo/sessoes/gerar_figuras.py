import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/ru_matplotlib')
from pathlib import Path
import csv,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse,Rectangle
P=Path(__file__).resolve().parent;out=P.parents[1]/'artigo/figuras';out.mkdir(exist_ok=True)
fig,ax=plt.subplots(figsize=(4.2,4.1),layout='constrained')
ax.add_patch(Rectangle((157,410),80,290,facecolor='#eeeeee',edgecolor='#999999'))
ax.text(197,548,'Mesa',rotation=90,ha='center',va='center',color='#555555')
for s,(x,y) in json.loads((P/'assentos.json').read_text())['anchors_hip_px'].items():
 ax.add_patch(Ellipse((x,y),54,40,edgecolor='#176582',facecolor='#c9e0e9',alpha=.9))
 ax.scatter(x,y,color='#176582',s=10);ax.text(53,y,s,ha='center',va='center')
ax.set(xlim=(30,250),ylim=(710,390),xlabel='Coordenada horizontal (pixel)',ylabel='Coordenada vertical (pixel)',title='Quatro regiões geométricas de assento')
ax.grid(alpha=.15);fig.savefig(out/'assentos.png',dpi=220);plt.close(fig)
refs=list(csv.DictReader((P/'referencias_temporais_ilustrativas.csv').open()))
cands={k:list(csv.DictReader((P/f'candidatas_{k}.csv').open())) for k in 'ABCD'}
fig,axs=plt.subplots(2,2,figsize=(10.5,5),layout='constrained')
for ax,r in zip(axs.flat,refs):
 start=float(r['start_mid']);end=float(r['end_mid']);left=start-90;right=end+90
 ax.broken_barh([((start-left)/60,(end-start)/60)],(3.7,.5),facecolors='#b3b3b3')
 for y,k,col in [(2.9,'A','#176582'),(2.1,'B','#d18b24'),(1.3,'C','#7061a4'),(.5,'D','#39836a')]:
  for c in cands[k]:
   a=float(c['start_s']);b=float(c['end_s'])
   if c['seat']==r['seat'] and b>left and a<right:
    ax.broken_barh([((max(a,left)-left)/60,(min(b,right)-max(a,left))/60)],(y,.5),facecolors=col)
 ax.set(xlim=(0,(right-left)/60),ylim=(0,4.4),title=f'{r["case"]}: {r["seat"]}, referência ≈ {float(r["duration_mid_min"]):g} min',xlabel='Minutos desde o início da janela')
 ax.set_yticks([3.95,3.15,2.35,1.55,.75],['Visual','A','B','C','D']);ax.grid(axis='x',alpha=.2)
fig.savefig(out/'contraste_temporal.png',dpi=220);plt.close(fig)
print('Figuras geradas')
