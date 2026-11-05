#!/usr/bin/env python3
"""Update a real build-plan task after its checklist evidence changes."""
import argparse,json,re
from datetime import datetime,timezone,timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser()
p.add_argument('task')
p.add_argument('--status',choices=['planned','working','review','done','blocked'])
p.add_argument('--completed',type=int)
p.add_argument('--phase')
p.add_argument('--note')
args=p.parse_args()
path=ROOT/'docs/build-plan.json';plan=json.loads(path.read_text())
task=next(t for t in plan['tasks'] if t['id']==args.task)
if args.completed is not None:
 if not 0<=args.completed<=len(task['steps']):raise SystemExit('Invalid completed step count')
 for i,step in enumerate(task['steps']):step['done']=i<args.completed
if args.status:task['status']=args.status
if task['status']=='done' and not all(s['done'] for s in task['steps']):raise SystemExit('A Done card must have every checklist step complete')
if args.note:task['note']=args.note
if args.phase:plan['phase']=args.phase
plan['updated']=datetime.now(timezone(timedelta(hours=7))).isoformat()
text=json.dumps(plan,indent=2,ensure_ascii=False)+'\n'
temp=path.with_suffix('.tmp');temp.write_text(text);temp.replace(path)
html=ROOT/'docs/build-board.html'
content=html.read_text()
embedded=json.dumps(plan,ensure_ascii=False).replace('<',r'\u003c')
content=re.sub(r'(<script id="initial-plan" type="application/json">).*?(</script>)',lambda m:m[1]+embedded+m[2],content,flags=re.S)
html.write_text(content)
done=sum(s['done'] for t in plan['tasks'] for s in t['steps'])
total=sum(len(t['steps']) for t in plan['tasks'])
print(f'{task["id"]}: {task["status"]}; overall {done}/{total} steps ({round(done/total*100)}%)')
