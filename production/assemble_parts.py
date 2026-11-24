"""Verify disjoint production outputs, encode the full course, retain screening."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path(__file__).resolve().parents[1];parts=sorted((R/'out/parts').glob('narration-part-*'));assert len(parts)==4
scenes=json.loads((R/'production/af-heart/scenes.json').read_text());byid={s['id']:s for s in scenes};raw=R/'production/af-heart/audio';raw.mkdir(parents=True,exist_ok=True)
durations={};reports={name:[]for name in ['narration-asr.json','narration-small-review.json']}
for part in parts:
 p=json.loads((part/'provenance.json').read_text())
 for name,sha in p['inputs'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha
 d=json.loads((part/'durations.json').read_text());assert d['voice']=='af_heart'and d['speed']==1.0
 assert not set(durations)&set(d['durations']);durations.update(d['durations'])
 for f in(part/'audio').glob('*.wav'):shutil.copy2(f,raw/f.name)
 for name in reports:reports[name].extend(json.loads((part/name).read_text())['clips'])
assert set(durations)==set(byid)
d['durations']=durations;(raw/'durations.json').write_text(json.dumps(d,indent=2)+'\n')
order={s['id']:i for i,s in enumerate(scenes)}
for name,rows in reports.items():
 assert len(rows)==len({x['id']for x in rows})
 if name=='narration-asr.json':assert {x['id']for x in rows}==set(byid)
 for row in rows:
  assert row['expected']==byid[row['id']]['text'];assert row['raw_sha256']==hashlib.sha256((raw/f"{row['id']}.wav").read_bytes()).hexdigest()
 rows.sort(key=lambda x:order[x['id']])
 (R/'qa'/name).write_text(json.dumps(dict(method='Independent tiny.en transcription of every clip, plus small.en flags and chapter samples. Four disjoint production jobs, four workers each. Not human listening approval.',clips=rows,flagged=sum(bool(x['flags'])for x in rows)),ensure_ascii=False,indent=2)+'\n')
assert {x['id']for x in reports['narration-asr.json']if x['flags']}<={x['id']for x in reports['narration-small-review.json']}
subprocess.run(['python3','production/encode_audio.py'],cwd=R,check=True)
p.pop('part');p['production_jobs']=4
(R/'qa/narration-ci-provenance.json').write_text(json.dumps(p,indent=2)+'\n')
print('All96 recordings merged, verified and encoded; review is required before publishing.',flush=True)
