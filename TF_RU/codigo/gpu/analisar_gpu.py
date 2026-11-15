"""Rastreamento integral e evidências para revisão; IDs não são sessões sentadas."""
import argparse
import csv
import json
import os
from pathlib import Path
import time

os.environ.setdefault('YOLO_CONFIG_DIR', str(Path(__file__).resolve().parent/'work'/'ultralytics'))
os.environ.setdefault('YOLO_AUTOINSTALL','false')

def doctor():
    import cv2, torch, ultralytics
    print(json.dumps({'torch':torch.__version__,'ultralytics':ultralytics.__version__,
        'opencv':cv2.__version__,'cuda':torch.cuda.is_available(),
        'gpu':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None},indent=2))
    if not torch.cuda.is_available():
        raise SystemExit('CUDA indisponível. Ative o Python com PyTorch/CUDA instalado antes de executar setup.sh.')

def run(a):
    import cv2, numpy as np, torch, ultralytics, yaml
    from ultralytics import YOLO
    from ultralytics.utils import ROOT as ULTRA_ROOT
    doctor()
    video=Path(a.video).resolve()
    if not video.is_file():raise SystemExit(f'Vídeo não encontrado: {video}')
    out=Path(a.output).resolve()
    out.mkdir(parents=True,exist_ok=True)
    if (out/'observacoes.jsonl').exists():
        raise SystemExit('Esta pasta já contém observações. Use outra pasta para preservar os resultados anteriores.')
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened():raise SystemExit('Não foi possível abrir o vídeo.')
    fps=cap.get(cv2.CAP_PROP_FPS);frame_count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps<=0:raise SystemExit('Taxa de quadros inválida.')
    tracker=yaml.safe_load((ULTRA_ROOT/'cfg/trackers/botsort.yaml').read_text())
    tracker.update(gmc_method='none',with_reid=False,track_buffer=max(1,round(a.gap/a.step)))
    (out/'tracker.yaml').write_text(yaml.safe_dump(tracker))
    model=YOLO(a.model)
    config=vars(a).copy()
    config.update(video=str(video),fps=fps,frame_count=frame_count,torch=torch.__version__,
        ultralytics=ultralytics.__version__,gpu=torch.cuda.get_device_name(0),
        scope='11:00–14:00, conforme informado pelo usuário; cobertura limitada à gravação e ao campo visível',
        note='IDs de rastreamento não identificam pessoas e não equivalem a sessões sentadas.')
    (out/'config.json').write_text(json.dumps(config,indent=2,ensure_ascii=False))
    (out/'versoes.txt').write_text(__import__('subprocess').check_output(
        [__import__('sys').executable,'-m','pip','freeze'],text=True))
    reviews=out/'revisao';reviews.mkdir(exist_ok=True)
    tracks={};n=0;idx=-1;target=0.;last=-1.;snapshot=-1;started=time.monotonic()
    completed=False
    try:
        with (out/'observacoes.jsonl').open('w') as f:
            while True:
                # grab preserva o percurso do arquivo; retrieve decodifica o quadro amostrado.
                if not cap.grab():
                    completed=True
                    break
                idx+=1
                t=cap.get(cv2.CAP_PROP_POS_MSEC)/1000
                # Tempos não monotônicos são erro, não se substituem silenciosamente por índice/fps.
                if idx>0 and t<=last:raise RuntimeError('Timestamp não crescente. Inspecione o arquivo antes de continuar.')
                last=t
                if t+1e-6<target:continue
                ok,frame=cap.retrieve()
                if not ok:raise RuntimeError(f'Falha ao decodificar quadro {idx}')
                # Grade fixa evita acumular o arredondamento entre frames e perder densidade.
                while target<=t+1e-6:target+=a.step
                r=model.track(frame,persist=True,tracker=str(out/'tracker.yaml'),device=0,
                    imgsz=a.imgsz,conf=a.conf,iou=.6,quantize=16,verbose=False)[0]
                boxes=r.boxes.xyxy.cpu().numpy()
                ids=r.boxes.id.cpu().numpy().astype(int) if r.boxes.id is not None else np.full(len(boxes),-1)
                keypoints=r.keypoints.data.cpu().numpy()
                confidences=r.boxes.conf.cpu().numpy()
                detections=[]
                for box,tid,k,c in zip(boxes,ids,keypoints,confidences):
                    tid=int(tid)
                    detections.append({'track_id':tid,'box':box.round(2).tolist(),
                        'confidence':float(c),'keypoints':k.round(3).tolist()})
                    if tid>=0:
                        rec=tracks.setdefault(tid,{'track_id':tid,'inicio_observado_s':t,'fim_observado_s':t,'observacoes':0})
                        rec['fim_observado_s']=t;rec['observacoes']+=1
                f.write(json.dumps({'frame':idx,'t':round(t,4),'detections':detections},separators=(',',':'))+'\n')
                n+=1
                slot=int(t//900)
                if slot!=snapshot:
                    cv2.imwrite(str(reviews/f'{t:010.3f}s.jpg'),r.plot(labels=False,line_width=1,kpt_radius=2))
                    snapshot=slot
                if n%120==0:
                    f.flush()
                    progress={'sampled_frames':n,'last_video_seconds':t,'elapsed_seconds':time.monotonic()-started}
                    (out/'progresso.json').write_text(json.dumps(progress))
                    print(json.dumps(progress),flush=True)
    finally:
        cap.release()
        # Divergência entre EOF e número esperado exige revisão: EOF também pode ser truncamento.
        if frame_count>0 and abs((idx+1)-frame_count)>2:completed=False
        result={'completed':completed,'sampled_frames':n,'read_frames':idx+1,
            'expected_frame_count':frame_count,'last_timestamp_s':last,'elapsed_seconds':time.monotonic()-started}
        (out/'conclusao.json').write_text(json.dumps(result,indent=2))
    fields=['track_id','inicio_observado_s','fim_observado_s','observacoes']
    with (out/'trechos_para_revisao.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(tracks.values())
    with (out/'sessoes_validadas_MODELO.csv').open('w') as f:
        csv.writer(f).writerow(['sessao','assento','inicio_s','fim_s','pausas_em_pe_s',
            'incompleta_inicio','incompleta_fim','validada'])
    (out/'LEIA_ANTES_DA_MEDIA.md').write_text('''# Revisão obrigatória da medição

O processamento cobre todo o arquivo. As caixas e IDs são observações de um rastreador, não sessões sentadas confirmadas. Uma pessoa pode ter múltiplos IDs; um ID pode ser associado à pessoa errada. Desaparecimento por oclusão não prova que alguém levantou. Não use a média dos comprimentos das trajetórias como tempo médio sentado.

Use o vídeo e `trechos_para_revisao.csv` para conferir sessões nos assentos com visibilidade suficiente. Em `sessoes_validadas_MODELO.csv`, crie uma linha por sessão, com segundos relativos ao início da gravação. Confirme o ato de sentar, o de levantar e as pausas em pé. Use 1/0 nos campos de incompletude e validação. Caso a visibilidade impeça confirmar um evento, mantenha a sessão sem validação. Registre separadamente os casos excluídos e sua causa.

Depois de preencher e renomear a tabela, execute o subcomando `resumir`. Ele só calcula tempos de sessões explicitamente validadas e completas. A média desse subconjunto pode ter viés de seleção; registre a cobertura espacial, temporal e a proporção de casos incompletos. Assentos mais fáceis de observar não representam automaticamente todo o RU.
''')
    if not completed:raise SystemExit('Cobertura incompleta. Verifique conclusao.json antes de usar os dados.')
    print('Arquivo completo percorrido; evidências prontas para revisão. Nenhuma média individual presumida.')

def resumir(a):
    import statistics
    with open(a.csv) as f:rows=list(csv.DictReader(f))
    if not rows:raise SystemExit('Tabela vazia: nenhuma sessão validada.')
    accepted=[];incomplete=0;unvalidated=0;groups={};seen=set();seat_intervals={}
    for row in rows:
        if not row['sessao'] or row['sessao'] in seen:raise SystemExit('Sessão vazia ou duplicada.')
        seen.add(row['sessao'])
        if row['validada'] not in ('0','1'):raise SystemExit('Preencha validada com 0 ou 1.')
        if row['validada']!='1':unvalidated+=1;continue
        if row['incompleta_inicio'] not in ('0','1') or row['incompleta_fim'] not in ('0','1'):
            raise SystemExit('Preencha incompletude com 0 ou 1.')
        if row['incompleta_inicio']=='1' or row['incompleta_fim']=='1':incomplete+=1;continue
        start,end,pause=map(float,(row['inicio_s'],row['fim_s'],row['pausas_em_pe_s']))
        if not (0<=start<end<=10798.357 and 0<=pause<=end-start):
            raise SystemExit(f'Tempos inválidos na sessão {row["sessao"]}')
        if not row['assento']:raise SystemExit('Informe o assento de cada sessão completa validada.')
        intervals=seat_intervals.setdefault(row['assento'],[])
        if any(start<b and end>a for a,b in intervals):raise SystemExit('Sessões completas sobrepostas no mesmo assento.')
        intervals.append((start,end))
        duration=(end-start-pause)/60
        accepted.append(duration);groups.setdefault(int(start//1800),[]).append(duration)
    def stats(v):return {'n':len(v),'media_min':statistics.mean(v),'mediana_min':statistics.median(v)} if v else {'n':0}
    result={'completas_validadas':stats(accepted),'incompletas_validadas':incomplete,
        'sem_validacao':unvalidated,'por_faixa_30min_do_inicio':{str(k):stats(v) for k,v in groups.items()},
        'limite':'Média condicionada a sessões completas e validadas; não generalizar automaticamente ao RU inteiro.'}
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor')
    r=sub.add_parser('run');r.add_argument('--video',required=True);r.add_argument('--output',default='work/integral')
    r.add_argument('--model',default='yolo11x-pose.pt');r.add_argument('--step',type=float,default=.5)
    r.add_argument('--imgsz',type=int,default=1280);r.add_argument('--conf',type=float,default=.15)
    r.add_argument('--gap',type=float,default=15)
    s=sub.add_parser('resumir');s.add_argument('--csv',required=True);s.add_argument('--output',default='resumo_validado.json')
    a=ap.parse_args()
    if a.command=='doctor':doctor()
    elif a.command=='run':
        if a.step<=0 or a.gap<0:ap.error('step deve ser positivo e gap não negativo')
        run(a)
    else:resumir(a)

if __name__=='__main__':main()
