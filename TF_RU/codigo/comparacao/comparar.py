import os
import json,csv,math,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
NEW=Path(os.environ['RU_ESTUDO'])
RUNS={'A_x_2fps_gap15':Path(os.environ['RU_BASELINE']),'B_m_2fps_gap15':NEW/'m_2fps_gap15','C_x_5fps_gap15':NEW/'x_5fps_gap15','D_x_2fps_gap5':NEW/'x_2fps_gap5'}
results=[];snapshots={};trackdetails={}
for name,path in RUNS.items():
 print('Lendo',name,flush=True)
 cfg=json.loads((path/'config.json').read_text());end=json.loads((path/'conclusao.json').read_text())
 assert end['completed'] and end['read_frames']==107981
 tracks={};count=0;total=0;last=-1;gap=0;bins=defaultdict(list);snap={}
 with (path/'observacoes.jsonl').open() as f:
  for line in f:
   o=json.loads(line);t=o['t'];assert t>last
   if last>=0:gap=max(gap,t-last)
   last=t;count+=1;ds=o['detections'];total+=len(ds);bins[int(t//1800)].append(len(ds))
   bucket=int(t//30)
   if bucket not in snap:snap[bucket]=o
   for d in ds:
    tid=d['track_id']
    if tid<0:continue
    b=d['box'];cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
    if tid not in tracks:tracks[tid]={'start':t,'end':t,'n':0,'maxgap':0,'xmin':cx,'xmax':cx,'ymin':cy,'ymax':cy,'first':{'t':t,'box':b}}
    tr=tracks[tid];tr['n']+=1;tr['maxgap']=max(tr['maxgap'],t-tr['end']);tr['end']=t
    tr['xmin']=min(tr['xmin'],cx);tr['xmax']=max(tr['xmax'],cx);tr['ymin']=min(tr['ymin'],cy);tr['ymax']=max(tr['ymax'],cy);tr['last']={'t':t,'box':b}
 assert count==end['sampled_frames']
 table=list(csv.DictReader((path/'trechos_para_revisao.csv').open()));assert len(table)==len(tracks)
 for row in table:
  tr=tracks[int(row['track_id'])]
  assert abs(tr['start']-float(row['inicio_observado_s']))<.001
  assert abs(tr['end']-float(row['fim_observado_s']))<.001
  assert tr['n']==int(row['observacoes'])
 spans=np.array([v['end']-v['start'] for v in tracks.values()])
 result={'experimento':name,'model':cfg['model'],'step':cfg['step'],'gap':cfg['gap'],'imagens':count,'ids':len(tracks),'ids_menos30s':int(sum(spans<30)),'percent_ids_menos30s':round(100*float(np.mean(spans<30)),2),'ids_10min_ou_mais':int(sum(spans>=600)),'mediana_intervalo_id_s':round(float(np.median(spans)),2),'deteccoes':total,'deteccoes_por_imagem':round(total/count,3),'maior_gap_amostragem_s':round(gap,4),'tempo_execucao_s':round(end['elapsed_seconds'],3),'faixas_30min':{str(k):{'n':len(v),'deteccoes_medias':sum(v)/len(v)} for k,v in bins.items()}}
 results.append(result);snapshots[name]=snap;trackdetails[name]=tracks
 print(json.dumps(result),flush=True)
(HERE/'comparacao.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
(HERE/'amostras_30s.json').write_text(json.dumps(snapshots,separators=(',',':')))
(HERE/'trajetorias_auditoria.json').write_text(json.dumps(trackdetails,separators=(',',':')))
fields=[k for k in results[0] if k!='faixas_30min']
with (HERE/'comparacao.csv').open('w') as f:
 w=csv.DictWriter(f,fields);w.writeheader();w.writerows({k:v for k,v in r.items() if k in fields} for r in results)
h=hashlib.sha256()
with open(os.environ['RU_VIDEO'],'rb') as f:
 for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
expected=(NEW/'video_sha256.txt').read_text().split()[0]
(HERE/'integridade_video.json').write_text(json.dumps({'local_sha256':h.hexdigest(),'server_sha256':expected,'match':h.hexdigest()==expected},indent=2))
assert h.hexdigest()==expected
print('Conferência de registros, tabelas e hash concluída.',flush=True)
