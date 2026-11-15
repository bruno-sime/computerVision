import os
"""Hipótese geométrica de ocupação: candidatos, não sessões validadas."""
import json,csv
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
ROOT=P.parent
NEW=Path(os.environ['RU_ESTUDO'])
RUNS={'A':Path(os.environ['RU_BASELINE']),'B':NEW/'m_2fps_gap15','C':NEW/'x_5fps_gap15','D':NEW/'x_2fps_gap5'}
SEATS={'S1':(131,651),'S2':(118,595),'S3':(110,548),'S4':(104,500)}
(P/'assentos.json').write_text(json.dumps({'image_size':[1280,720],'anchors_hip_px':SEATS,'radius_px':[27,20],'keypoint_conf':.4,'min_shoulder_hip_dy':25,'note':'Regiões definidas geometricamente na câmera; cadeira móvel e perspectiva impõem incerteza. Não há identificação facial.'},indent=2))
for name,path in RUNS.items():
 print('Assentos',name,flush=True)
 rows=[];lastbucket=-1
 with (path/'observacoes.jsonl').open() as f:
  for line in f:
   o=json.loads(line);b=int(o['t']//5)
   if b==lastbucket:continue
   lastbucket=b
   candidates=[]
   for d in o['detections']:
    k=np.array(d['keypoints']);hip=k[[11,12]];shoulder=k[[5,6]]
    if (hip[:,2]>=.4).sum()<1 or (shoulder[:,2]>=.4).sum()<1:continue
    xy=np.average(hip[hip[:,2]>=.4,:2],axis=0,weights=hip[hip[:,2]>=.4,2]);sh=np.average(shoulder[shoulder[:,2]>=.4,:2],axis=0,weights=shoulder[shoulder[:,2]>=.4,2])
    if xy[1]-sh[1]<25:continue
    for seat,(x,y) in SEATS.items():
     dist=((xy[0]-x)/27)**2+((xy[1]-y)/20)**2
     if dist<=1:candidates.append((dist,seat,d,xy.tolist(),sh.tolist()))
   used=set();selected={}
   for dist,seat,d,hip,sh in sorted(candidates,key=lambda q:q[0]):
    if seat not in selected and d['track_id'] not in used:
     selected[seat]={'id':d['track_id'],'hips':hip,'shoulders':sh,'keypoints':d['keypoints'],'score':d['confidence']};used.add(d['track_id'])
   rows.append({'t':o['t'],'bucket':b,'seats':selected})
 (P/f'assentos_{name}.json').write_text(json.dumps(rows,separators=(',',':')))
 print(name,len(rows),flush=True)
