"""Checagens diagnósticas; referências assistidas, sem teste humano independente."""
from pathlib import Path
import csv,json
P=Path(__file__).resolve().parent
truth=list(csv.DictReader((P/'referencia_visual_pontual.csv').open()))
refs=list(csv.DictReader((P/'referencias_temporais_ilustrativas.csv').open()))
metrics=[]
for k in 'ABCD':
 rows=json.loads((P/f'assentos_{k}.json').read_text());tp=tn=fp=fn=0
 for r in truth:
  row=min(rows,key=lambda v:abs(v['t']-float(r['t_s'])));true=int(r['ocupado_referencia']);pred=int(r['assento'] in row['seats'])
  tp+=int(pred and true);tn+=int(not pred and not true);fp+=int(pred and not true);fn+=int(not pred and true)
 metrics.append(dict(config=k,n=len(truth),true_positive=tp,true_negative=tn,false_positive=fp,false_negative=fn,correct=tp+tn,note='Checagem pontual assistida; não valida duração e não é teste independente.'))
 cand=list(csv.DictReader((P/f'candidatas_{k}.csv').open()));out=[]
 for r in refs:
  start=float(r['start_mid']);end=float(r['end_mid']);parts=[]
  for c in cand:
   if c['seat']!=r['seat']:continue
   inter=max(0,min(float(c['end_s']),end)-max(float(c['start_s']),start))
   if inter>0:parts.append(inter)
  out.append(dict(case=r['case'],overlapping_candidates=len(parts),reference_mid_minutes=float(r['duration_mid_min']),covered_reference_seconds=sum(parts),largest_overlap_seconds=max(parts,default=0)))
 (P/f'contraste_temporal_{k}.json').write_text(json.dumps(out,indent=2))
(P/'checagem_pontual.json').write_text(json.dumps(metrics,indent=2))
print('Referências pontuais e contrastes recalculados.')
