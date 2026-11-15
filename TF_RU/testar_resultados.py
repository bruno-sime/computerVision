"""Valida integridade tabular e coerência dos intervalos, sem declarar acurácia."""
from pathlib import Path
import csv,json,math
P=Path(__file__).resolve().parent
summary=json.loads((P/'resultados/resumo_candidatas.json').read_text())
for k in 'ABCD':
 rows=list(csv.DictReader((P/f'resultados/candidatas_{k}.csv').open()));prev={}
 for row in rows:
  a,b,span=map(float,[row['start_s'],row['end_s'],row['span_s']])
  assert 0<=a<b<=10798.357
  assert abs(span-(b-a))<.001 and span>=60
  assert a>=prev.get(row['seat'],-1),'Intervalos sobrepostos no mesmo assento'
  assert row['status']=='candidata_nao_validada'
  prev[row['seat']]=b
 full=[r for r in rows if r['incomplete_start']=='0' and r['incomplete_end']=='0']
 expected=next(r for r in summary if r['config']==k)
 assert expected['candidate_count']==len(rows)
 assert expected['complete_candidates']==len(full)
 assert math.isclose(expected['mean_span_min'],sum(float(r['span_s']) for r in full)/len(full)/60)
 comparisons=json.loads((P/'resultados/comparacao.json').read_text())
 assert next(r for r in comparisons if r['experimento'].startswith(k+'_'))['imagens'] in [21597,53992]
 assert json.loads((P/f'resultados/configuracoes/{k}/conclusao.json').read_text())['completed']
print('OK: cobertura registrada, limites temporais, ausência de sobreposição, contagens e médias dos candidatos.')
print('Estes testes não validam identidade nem duração sentada real.')
