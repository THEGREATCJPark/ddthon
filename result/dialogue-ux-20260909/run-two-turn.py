"""Operator-assisted two-turn acceptance. Not a user conversation or product code."""
import hashlib, json, os, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
def now(): return datetime.now(timezone.utc).isoformat()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def visible(x):
    if isinstance(x, dict):
        return {k: visible(v) for k,v in x.items() if k not in ('thinking','signature')}
    if isinstance(x, list):
        return [visible(v) for v in x if not isinstance(v,dict) or v.get('type') not in ('thinking','redacted_thinking')]
    return x

def turn(number, prompt, workspace, private, settings, env, session=None):
    raw = private/f'turn-{number}.jsonl'
    command = [str(Path.home()/'.local/bin/claude.exe'), '-p', prompt,
               '--output-format','stream-json','--verbose','--permission-mode','dontAsk',
               '--settings',str(settings),'--tools','Read,Glob,Grep,Bash,Skill,Write,Edit']
    if session: command += ['--resume',session]
    else: command += ['--append-system-prompt',
        '현재 workspace 업무만 수행. 제품 소스/외부 사전 구현/다른 작업공간/암호/인증정보 접근 금지. '
        '제품 CLI 도움말은 확인 가능. 원본을 저장/수정하지 않는다. 사람 review/게시를 대신 만들지 않는다.']
    started = now()
    with raw.open('w',encoding='utf-8') as stdout, (OUT/f'p1-turn-{number}-stderr.txt').open('w',encoding='utf-8') as stderr:
        proc = subprocess.Popen(command,cwd=workspace,stdout=stdout,stderr=stderr,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
        try: code = proc.wait(timeout=600)
        except subprocess.TimeoutExpired: proc.kill(); proc.wait(); code='TIMEOUT'
    events = [visible(json.loads(line)) for line in raw.read_text(encoding='utf-8').splitlines() if line.strip()]
    save(OUT/f'p1-turn-{number}-trace.json',events)
    lines = [f'# P1 turn {number} — operator supplied user input',prompt]
    texts=[]; tools=[]
    for ev in events:
        msg=ev.get('message',{}); content=msg.get('content',[]) if isinstance(msg,dict) else []
        if isinstance(content,str): content=[{'type':'text','text':content}]
        for b in content:
            if b.get('type')=='text':
                lines += [f"\n{msg.get('role',ev.get('type'))}:\n{b['text']}"]
                if ev.get('type')=='assistant': texts.append(b['text'])
            elif b.get('type')=='tool_use': lines += ['\nTool '+b['name']+'\n```json\n'+json.dumps(b['input'],ensure_ascii=False,indent=2)+'\n```']
            elif b.get('type')=='tool_result':
                value=b.get('content',''); value=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)
                tools.append(value);lines += ['\nTool result (error='+str(b.get('is_error',False))+')\n```text\n'+value+'\n```']
    (OUT/f'p1-turn-{number}-transcript.md').write_text('\n'.join(lines),encoding='utf-8')
    (OUT/f'p1-turn-{number}-responses.md').write_text('\n\n'.join(texts),encoding='utf-8')
    reports=[]
    for value in tools:
        for i,c in enumerate(value):
            if c!='{': continue
            try: report,_=json.JSONDecoder().raw_decode(value[i:])
            except ValueError: continue
            if isinstance(report,dict) and 'status' in report and ('trace' in report or 'work' in report): reports.append(report);break
    save(OUT/f'p1-turn-{number}-reports.json',reports)
    sid=next((ev.get('session_id') for ev in events if ev.get('session_id')),None)
    return {'started_at':started,'finished_at':now(),'exit_code':code,'session_id':sid,
            'reports':reports,'prompt':prompt,'responses':texts}

def main():
    if (OUT/'p1-status.json').exists(): raise FileExistsError('Preserve the first run')
    workspace=Path.home()/'Desktop'/('skillloop-two-turn-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    private=Path(os.environ['TEMP'])/workspace.name;private.mkdir()
    env=os.environ.copy();env['PYTHONUTF8']='1';env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env['PATH']
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    with (OUT/'p1-prepare.txt').open('w',encoding='utf-8') as log:
        helper=subprocess.Popen([sys.executable,str(ROOT/'scripts/prepare-p1.py'),str(workspace)],stdout=log,stderr=subprocess.STDOUT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline=time.monotonic()+120
            while not (workspace/'ready.json').exists() and helper.poll() is None and time.monotonic()<deadline: time.sleep(1)
            if not (workspace/'ready.json').exists(): raise RuntimeError('Excel not ready')
            work=workspace/'warm'  # different layout; no shared Skill is pulled: this is Cold
            ctx=load(work/'skillloop-work.json');xlsx=next(work.glob('*.xlsx'))
            settings=OUT/'p1-permissions.json';save(settings,load(ROOT/'result/scenario-correction/cold-agent-settings.local.json'))
            state={'source_sha':source,'workspace':str(work),'ready':load(workspace/'ready.json'),
                   'private_logs':str(private),'hash_before':sha(xlsx),'store_before':load(Path(ctx['store'])),
                   'usage_before':load(Path(ctx['usage'])),'operator_assisted':True,'turns':[]}
            save(OUT/'p1-status.json',state)
            first=turn(1,xlsx.name+'를 읽고 다음달 예상 생산량을 포함한 추세선을 보여줘.',work,private,settings,env)
            state['turns'].append(first)
            state['store_after_turn1']=load(Path(ctx['store']));state['usage_after_turn1']=load(Path(ctx['usage']))
            save(OUT/'p1-status.json',state)
            if not first['session_id'] or first['exit_code']!=0: raise RuntimeError('First turn failed')
            second=turn(2,'이상하네, 난 엑셀을 열어서 데이터를 볼 수 있는데? 한번 다른 방법으로 진행해봐.',work,private,settings,env,first['session_id'])
            state['turns'].append(second)
            state.update(hash_after=sha(xlsx),store=load(Path(ctx['store'])),usage=load(Path(ctx['usage'])))
            state['charts']=[]
            for p in (work/'.skillloop/artifacts').glob('*-trend.png'):
                dest=OUT/('p1-'+p.name);shutil.copyfile(p,dest);state['charts'].append(dest.name)
            save(OUT/'p1-status.json',state)
            print('Two-turn run finished; inspect reports and original transcript',flush=True)
        finally:
            if workspace.exists(): (workspace/'STOP').touch()
            try: helper.wait(timeout=45)
            except subprocess.TimeoutExpired: print('Owned Excel cleanup pending; no global termination',flush=True)

if __name__=='__main__': main()
