"""Render and screen narration on a build runner; this workflow never publishes a site."""
from pathlib import Path
import subprocess,json,os,shutil,hashlib,urllib.request,concurrent.futures
R=Path(__file__).resolve().parents[1];OUT=R/'out/narration';OUT.mkdir(parents=True,exist_ok=True);TOOLS=OUT/'tools';TOOLS.mkdir(exist_ok=True)
PIN='https://raw.githubusercontent.com/snowch/claude-skills/c9a7c521568632aa216932f4c965df386498602a/plugins/demo-video/skills/record-demo/scripts/'
HASHES={'tts.py':'42144c38b2840c7877bd3d514ad368cc81bfd278a53a63925e23caa3af4669a5','speech_backend.py':'7850f8c06735769bb4e163acd3f3a2d005968a12d63c815441c9442ba4c78cd4'}
for name,digest in HASHES.items():
 data=urllib.request.urlopen(PIN+name,timeout=90).read();assert hashlib.sha256(data).hexdigest()==digest; (TOOLS/name).write_bytes(data)
scenes=json.loads((R/'production/af-heart/scenes.json').read_text());env=os.environ.copy();env.update(DEMO_TTS_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONUNBUFFERED='1')
# Download and verify the shared model once before concurrent readers start.
warm=OUT/'warmup';warm.mkdir(exist_ok=True);(warm/'scenes.json').write_text('[]')
subprocess.run(['uv','run',str(TOOLS/'tts.py'),str(warm),'af_heart','1.0'],cwd=R,env=env,check=True)
workers=4;buckets=[[]for _ in range(workers)];loads=[0]*workers
for s in sorted(scenes,key=lambda s:len(s['say']),reverse=True):
 i=loads.index(min(loads));buckets[i].append(s);loads[i]+=len(s['say'])
def render(i):
 d=OUT/f'worker-{i}';d.mkdir(exist_ok=True);(d/'scenes.json').write_text(json.dumps(buckets[i],ensure_ascii=False));
 with (d/'synthesis.log').open('w')as log:subprocess.run(['uv','run',str(TOOLS/'tts.py'),str(d),'af_heart','1.0'],cwd=R,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
 return d
with concurrent.futures.ThreadPoolExecutor(workers)as pool:dirs=list(pool.map(render,range(workers)))
raw=R/'production/af-heart/audio';raw.mkdir(parents=True,exist_ok=True);durations={};provenance=None
for d in dirs:
 provenance=json.loads((d/'audio/durations.json').read_text());durations.update(provenance['durations'])
 for f in (d/'audio').glob('*.wav'):shutil.copy2(f,raw/f.name)
assert set(durations)=={s['id']for s in scenes};provenance['durations']=durations;(raw/'durations.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('Synthesized',len(durations),'clips.',flush=True)
subprocess.run(['python3','production/encode_audio.py'],cwd=R,env=env,check=True)
def screen(i):
 report=OUT/f'screen-{i}';report.mkdir(exist_ok=True)
 with (report/'screen.log').open('w')as log:subprocess.run(['uv','run','scripts/screen_narration.py','--threads','1','--shards',str(workers),'--shard',str(i),'--report-dir',str(report)],cwd=R,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
 return report
with concurrent.futures.ThreadPoolExecutor(workers)as pool:reports=list(pool.map(screen,range(workers)))
for name in ['narration-asr.json','narration-small-review.json']:
 rows=[row for report in reports for row in json.loads((report/name).read_text())['clips']];assert len({row['id']for row in rows})==len(rows)
 order={s['id']:i for i,s in enumerate(scenes)};rows.sort(key=lambda row:order[row['id']])
 if name=='narration-asr.json':assert len(rows)==96
 (R/'qa'/name).write_text(json.dumps(dict(method='Independent tiny.en full screening plus small.en checks of flags and chapter samples, run in disjoint shards. Not human listening approval.',clips=rows,flagged=sum(bool(row.get('flags'))for row in rows)),ensure_ascii=False,indent=2)+'\n')
inputs={name:hashlib.sha256((R/name).read_bytes()).hexdigest()for name in ['course.json','production/af-heart/scenes.json']}
(R/'qa/narration-ci-provenance.json').write_text(json.dumps(dict(commit=os.environ.get('GITHUB_SHA'),run_id=os.environ.get('GITHUB_RUN_ID'),inputs=inputs,voice='af_heart',speed=1.0,render_workers=workers),indent=2)+'\n')
print('All96 clips independently screened; review flags before publishing.',flush=True)
