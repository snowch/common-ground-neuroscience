# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["faster-whisper", "soundfile", "numpy"]
# ///
"""Transcribe course WAVs independently and recheck flags plus chapter samples."""
from pathlib import Path
import argparse,difflib,hashlib,json,re
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--model',default='tiny.en');p.add_argument('--review-model',default='small.en');p.add_argument('--threads',type=int,default=1);p.add_argument('--shards',type=int,default=1);p.add_argument('--shard',type=int,default=0);p.add_argument('--report-dir',default='qa');args=p.parse_args()
report_dir=(R/args.report_dir).resolve();report_dir.mkdir(parents=True,exist_ok=True)
scenes=json.loads((R/'production/af-heart/scenes.json').read_text());pause=re.compile(r'\[pause(?:\s+([\d.]+))?\]')
if args.shards>1:
 buckets=[[]for _ in range(args.shards)];loads=[0]*args.shards
 for scene in sorted(scenes,key=lambda s:len(s['text']),reverse=True):
  i=loads.index(min(loads));buckets[i].append(scene['id']);loads[i]+=len(scene['text'])
 selected=set(buckets[args.shard]);scenes=[s for s in scenes if s['id']in selected]
from speech_text import words
def check(scene,model,name):
 path=R/'production/af-heart/audio'/f"{scene['id']}.wav"
 if not path.exists():raise SystemExit(f'Generate raw speech first: {path}')
 data,sr=sf.read(path,dtype='float32');duration=len(data)/sr
 sample=np.interp(np.arange(0,duration,1/16000),np.arange(len(data))/sr,data).astype(np.float32)
 segments,_=model.transcribe(sample,language='en',beam_size=5,condition_on_previous_text=False)
 heard=' '.join(s.text.strip()for s in segments);ratio=difflib.SequenceMatcher(None,words(scene['text']),words(heard),autojunk=False).ratio()
 pauses=sum(float(x or .5)for x in pause.findall(scene.get('say',scene['text'])));wpm=len(words(scene['text']))/max(.1,duration-pauses)*60
 flags=[]
 if ratio<.9:flags.append('words')
 if wpm<120 or wpm>190:flags.append('pace')
 peak=float(np.max(np.abs(data)))
 if peak>=.99:flags.append('peak')
 return dict(id=scene['id'],expected=scene['text'],heard=heard,ratio=round(ratio,4),model=name,duration=round(duration,3),wpm=round(wpm,1),peak=peak,flags=flags,raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
report_path=report_dir/'narration-asr.json'
retained={x['id']:x for x in json.loads(report_path.read_text())['clips']} if report_path.exists() else {}
model=WhisperModel(args.model,device='cpu',compute_type='int8',cpu_threads=args.threads,num_workers=1);rows=[]
for scene in scenes:
 raw=R/'production/af-heart/audio'/f"{scene['id']}.wav";old=retained.get(scene['id'])
 row=old if old and old['expected']==scene['text'] and old['raw_sha256']==hashlib.sha256(raw.read_bytes()).hexdigest() else check(scene,model,args.model);row['ratio']=round(difflib.SequenceMatcher(None,words(row['expected']),words(row['heard']),autojunk=False).ratio(),4);row['flags']=[f for f in row['flags'] if f!='words']+(['words'] if row['ratio']<.9 else []);rows.append(row)
 (report_dir/'narration-asr.json').write_text(json.dumps(dict(method='Independent transcription of raw synthesized speech; not human listening approval.',clips=rows,flagged=sum(bool(x['flags'])for x in rows)),ensure_ascii=False,indent=2)+'\n')
 print(row['id'],row['ratio'],row['flags'],flush=True)
del model
review_model=WhisperModel(args.review_model,device='cpu',compute_type='int8',cpu_threads=args.threads,num_workers=1)
targets={row['id']for row in rows if row['flags']}|{f'c{i:02d}s03'for i in range(1,7)}
review_path=report_dir/'narration-small-review.json';prior={x['id']:x for x in json.loads(review_path.read_text())['clips']} if review_path.exists() else {}
reviews=[]
for scene in scenes:
 if scene['id']not in targets:continue
 raw=R/'production/af-heart/audio'/f"{scene['id']}.wav";old=prior.get(scene['id'])
 reviews.append(old if old and old['expected']==scene['text'] and old['raw_sha256']==hashlib.sha256(raw.read_bytes()).hexdigest() else check(scene,review_model,args.review_model))
(report_dir/'narration-small-review.json').write_text(json.dumps(dict(method='Additional independent transcription of flagged clips and chapter explanation samples; not listening approval.',clips=reviews),ensure_ascii=False,indent=2)+'\n')
print('Review flagged words, numbers, pace and phonemes before publishing. Transcription agreement is not human listening approval.')
