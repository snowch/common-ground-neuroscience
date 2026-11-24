"""Produce one disjoint quarter of the course; do not publish a site."""
from pathlib import Path
import concurrent.futures,hashlib,json,os,shutil,subprocess,sys,urllib.request
R=Path(__file__).resolve().parents[1];part=int(sys.argv[1]);assert part in range(4)
OUT=R/'out'/f'part-{part}';OUT.mkdir(parents=True,exist_ok=True);TOOLS=R/'out/tools';TOOLS.mkdir(exist_ok=True)
PIN='https://raw.githubusercontent.com/snowch/claude-skills/c9a7c521568632aa216932f4c965df386498602a/plugins/demo-video/skills/record-demo/scripts/'
HASHES={'tts.py':'42144c38b2840c7877bd3d514ad368cc81bfd278a53a63925e23caa3af4669a5','speech_backend.py':'7850f8c06735769bb4e163acd3f3a2d005968a12d63c815441c9442ba4c78cd4'}
for name,digest in HASHES.items():
 data=urllib.request.urlopen(PIN+name,timeout=90).read();assert hashlib.sha256(data).hexdigest()==digest;(TOOLS/name).write_bytes(data)
scenes=json.loads((R/'production/af-heart/scenes.json').read_text());buckets=[[]for _ in range(16)];loads=[0]*16
# Exactly the partition used by screen_narration.py.
for scene in sorted(scenes,key=lambda s:len(s['text']),reverse=True):
 i=loads.index(min(loads));buckets[i].append(scene);loads[i]+=len(scene['text'])
indices=list(range(part*4,part*4+4));env=os.environ.copy();env.update(DEMO_TTS_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONUNBUFFERED='1')
warm=R/'out/warm';warm.mkdir(exist_ok=True);(warm/'scenes.json').write_text('[]')
subprocess.run(['uv','run',str(TOOLS/'tts.py'),str(warm),'af_heart','1.0'],env=env,check=True)
def render(i):
 d=R/'out'/f'worker-{i}';d.mkdir(exist_ok=True);(d/'scenes.json').write_text(json.dumps(buckets[i],ensure_ascii=False))
 with(d/'synthesis.log').open('w')as log:subprocess.run(['uv','run',str(TOOLS/'tts.py'),str(d),'af_heart','1.0'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 return d
with concurrent.futures.ThreadPoolExecutor(4)as pool:dirs=list(pool.map(render,indices))
raw=R/'production/af-heart/audio';raw.mkdir(parents=True,exist_ok=True);(OUT/'audio').mkdir(exist_ok=True);durations={}
for d in dirs:
 provenance=json.loads((d/'audio/durations.json').read_text());durations.update(provenance['durations'])
 for f in(d/'audio').glob('*.wav'):shutil.copy2(f,raw/f.name);shutil.copy2(f,OUT/'audio'/f.name)
provenance['durations']=durations;(OUT/'durations.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('Part',part,'synthesized',len(durations),'clips',flush=True)
# Warm both independent decoders once, before concurrent readers start.
warm_script=R/'out/warm_models.py';warm_script.write_text('# /// script\n# dependencies = ["faster-whisper"]\n# ///\nfrom faster_whisper import WhisperModel\nfor name in ["tiny.en","small.en"]:\n m=WhisperModel(name,device="cpu",compute_type="int8",cpu_threads=1);del m\n')
subprocess.run(['uv','run',str(warm_script)],env=env,check=True)
def screen(i):
 d=R/'out'/f'screen-{i}';d.mkdir(exist_ok=True)
 with(d/'screen.log').open('w')as log:subprocess.run(['uv','run','scripts/screen_narration.py','--threads','1','--shards','16','--shard',str(i),'--report-dir',str(d)],cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 return d
with concurrent.futures.ThreadPoolExecutor(4)as pool:reports=list(pool.map(screen,indices))
for name in ['narration-asr.json','narration-small-review.json']:
 rows=[row for d in reports for row in json.loads((d/name).read_text())['clips']]
 assert len(rows)==len({row['id']for row in rows})
 (OUT/name).write_text(json.dumps(dict(clips=rows),ensure_ascii=False,indent=2)+'\n')
inputs={name:hashlib.sha256((R/name).read_bytes()).hexdigest()for name in ['course.json','production/af-heart/scenes.json']}
(OUT/'provenance.json').write_text(json.dumps(dict(commit=os.environ.get('GITHUB_SHA'),run_id=os.environ.get('GITHUB_RUN_ID'),part=part,inputs=inputs,voice='af_heart',speed=1.0,render_workers_per_job=4),indent=2)+'\n')
print('Part',part,'independently screened',flush=True)
