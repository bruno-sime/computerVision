import os
"""Segmentação exploratória por geometria e cor da roupa; sem reconhecimento facial."""
from pathlib import Path
import json,subprocess,csv
import cv2,numpy as np
P=Path(__file__).resolve().parent
rows={k:json.loads((P/f'assentos_{k}.json').read_text()) for k in 'ABCD'}
if not (P/'cores.json').exists():
 cap=cv2.VideoCapture(os.environ['RU_VIDEO'])
 assert cap.isOpened()
 colors={k:[] for k in 'ABCD'};idx=0
 while cap.grab():
  actual_t=cap.get(cv2.CAP_PROP_POS_MSEC)/1000
  if actual_t+1e-6<idx*5:continue
  ok,im=cap.retrieve();assert ok
  for k in 'ABCD':
   item=rows[k][idx];cur={}
   for seat,d in item['seats'].items():
    kp=np.array(d['keypoints']);poly=kp[[5,6,12,11],:2].astype(np.int32)
    mask=np.zeros((720,1280),np.uint8);cv2.fillPoly(mask,[poly],255);mask=cv2.erode(mask,np.ones((3,3),np.uint8))
    yy,xx=np.where(mask)
    if len(xx)<20:continue
    # Cor da roupa: pixels do torso delimitado pelos pontos corporais.
    pix=im[yy,xx].reshape(-1,1,3);lab=cv2.cvtColor(pix,cv2.COLOR_BGR2LAB).reshape(-1,3)
    cur[seat]={'lab':np.median(lab,axis=0).tolist(),'track_id':d['id']}
   colors[k].append(cur)
  idx+=1
  if idx%360==0:print('Cor',idx,flush=True)
 cap.release()
 assert idx==2160
 (P/'cores.json').write_text(json.dumps(colors,separators=(',',':')))
else:colors=json.loads((P/'cores.json').read_text())
results=[]
for k in 'ABCD':
 episodes=[]
 for seat in ['S1','S2','S3','S4']:
  active=[];history=[];pending=[];lastidx=None
  def emit(segment):
   if not segment:return
   start=segment[0]*5;end=min(segment[-1]*5+5,10798.357)
   if end-start>=60:
    episodes.append({'config':k,'seat':seat,'start_s':start,'end_s':end,'span_s':end-start,
      'observed_support_s':len(segment)*5,'support_fraction':len(segment)*5/(end-start),
      'incomplete_start':int(start==0),'incomplete_end':int(segment[-1]==2159),'status':'candidata_nao_validada'})
  for i,ob in enumerate(colors[k]):
   d=ob.get(seat)
   if d is None:
    if active and i-lastidx>2:
     emit(active);active=[];history=[];pending=[]
    continue
   lab=np.array(d['lab'])
   if active and i-lastidx>2:
    emit(active);active=[];history=[];pending=[]
   lastidx=i
   if not active:active=[i];history=[lab];continue
   distance=np.linalg.norm(lab-np.median(history[-6:],axis=0))
   if distance>35:
    pending.append((i,lab))
    if len(pending)>=3:
     emit(active);active=[j for j,_ in pending];history=[c for _,c in pending];pending=[]
   else:
    active.extend(j for j,_ in pending);history.extend(c for _,c in pending);pending=[]
    active.append(i);history.append(lab)
  emit(active)
 episodes.sort(key=lambda v:(v['seat'],v['start_s']))
 with (P/f'candidatas_{k}.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(episodes[0]));w.writeheader();w.writerows(episodes)
 complete=[v for v in episodes if not v['incomplete_start'] and not v['incomplete_end']]
 results.append({'config':k,'candidate_count':len(episodes),'complete_candidates':len(complete),'mean_span_min':float(np.mean([v['span_s']/60 for v in complete])),'median_span_min':float(np.median([v['span_s']/60 for v in complete])),'note':'Intervalos candidatos de ocupação: não média validada de estudantes.'})
 print(results[-1],flush=True)
(P/'resumo_candidatas.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
