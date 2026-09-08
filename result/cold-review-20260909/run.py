"""Operator-only fresh Agent acceptance run; never a product recovery step."""
import hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from tests.prepare_p0_work import prepare_work

def sanitize(x):
    if isinstance(x, dict):
        if x.get('type') in ('thinking', 'redacted_thinking'):
            return None
        return {k: sanitize(v) for k, v in x.items() if k not in ('thinking', 'signature')}
    if isinstance(x, list):
        return [sanitize(v) for v in x if not isinstance(v, dict) or v.get('type') not in ('thinking', 'redacted_thinking')]
    return x

def now(): return datetime.now(timezone.utc).isoformat()
def save(p, obj): p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def run_agent(name, work, source, prompt, private):
    ctx = load(work/'skillloop-work.json')
    settings = load(ROOT/'result/scenario-correction/cold-agent-settings.local.json')
    for key in ('product_python', 'work_python'):
        for path in (ctx[key], Path(ctx[key]).as_posix()):
            settings['permissions']['allow'] += [f'Bash("{path}" *)', f'Bash({path} *)']
    setting_path = OUT/(name+'-permissions.json'); save(setting_path, settings)
    constraint = ('현재 workspace 업무만 수행. 제품 소스, 외부 사전 구현 Reference, 다른 workspace, 암호/인증정보를 읽거나 수정하지 않는다. '
                  '제품 CLI --help와 실제 오류는 확인 가능. 원본 문서를 수정/저장하지 않는다. 사람 승인/게시를 대신 만들지 않는다. '
                  '정상 실행 중 도구 오류는 정직하게 보고하고 현재 계약에서 해결한다.')
    cmd = [str(Path.home()/'.local/bin/claude.exe'), '-p', prompt, '--output-format', 'stream-json', '--verbose',
           '--permission-mode', 'dontAsk', '--settings', str(setting_path), '--tools', 'Read,Glob,Grep,Bash,Skill,Write,Edit',
           '--append-system-prompt', constraint]
    raw = private/(name+'.jsonl')
    state = {'started_at': now(), 'prompt': prompt, 'workspace': str(work), 'source_sha': source,
             'pre_store': load(Path(ctx['store'])), 'pre_usage': load(Path(ctx['usage'])),
             'input_hash_before': sha(work/('requirements.txt' if name=='p0' else next(work.glob('*.xlsx')).name)),
             'raw_private_log': str(raw)}
    env = os.environ.copy(); env['PYTHONUTF8']='1'; env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env['PATH']
    with raw.open('w',encoding='utf-8') as out, (OUT/(name+'-stderr.txt')).open('w',encoding='utf-8') as err:
        process = subprocess.Popen(cmd,cwd=work,stdout=out,stderr=err,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
        state['pid']=process.pid; save(OUT/(name+'-status.json'),state)
        try: state['exit_code']=process.wait(timeout=600)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(); state['exit_code']='TIMEOUT'
    events=[]
    for line in raw.read_text(encoding='utf-8').splitlines():
        try: events.append(sanitize(json.loads(line)))
        except ValueError: events.append({'unparsed':line})
    save(OUT/(name+'-trace.json'),events)
    transcript=[f'# {name} complete visible transcript',f'User: {prompt}']
    for ev in events:
        if not isinstance(ev,dict): continue
        msg=ev.get('message',{})
        content=msg.get('content',[]) if isinstance(msg,dict) else []
        if isinstance(content,str): transcript.append(content);continue
        for b in content:
            if b.get('type')=='text':transcript.append('\n'+str(msg.get('role',ev.get('type','message')))+':\n'+b.get('text',''))
            elif b.get('type')=='tool_use':transcript.append('\nTool '+b.get('name','')+' input:\n```json\n'+json.dumps(b.get('input'),ensure_ascii=False,indent=2)+'\n```')
            elif b.get('type')=='tool_result':transcript.append('\nTool result (error='+str(b.get('is_error',False))+'):\n```text\n'+str(b.get('content',''))+'\n```')
        if ev.get('type')=='result':transcript.append('\nFinal result:\n'+str(ev.get('result','')))
    (OUT/(name+'-transcript.md')).write_text('\n'.join(transcript),encoding='utf-8')
    state.update(finished_at=now(),store=load(Path(ctx['store'])),usage=load(Path(ctx['usage'])))
    state['input_hash_after']=sha(work/('requirements.txt' if name=='p0' else next(work.glob('*.xlsx')).name))
    state['original_unchanged']=state['input_hash_before']==state['input_hash_after']
    state['charts']=[]
    for chart in (work/'.skillloop/artifacts').glob('*-trend.png'):
        dest=OUT/(name+'-'+chart.name);shutil.copyfile(chart,dest);state['charts'].append(dest.name)
    if name=='p0':
        result=subprocess.run([ctx['work_python'],'-c',"import importlib.metadata as m; import skillloop_demo_pkg; print(m.version('skillloop-demo-pkg'))"],capture_output=True,text=True,env=env)
        state['independent_import']={'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    save(OUT/(name+'-status.json'),state)
    print(name+' completed: exit='+str(state['exit_code'])+' charts='+str(len(state['charts'])),flush=True)

def main():
    global OUT
    if len(sys.argv)>1:
        OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=False)
    if any(OUT.glob('*-status.json')):
        raise FileExistsError('Preserve previous logs; supply a new output directory argument')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    workspace=Path.home()/'Desktop'/('skillloop-cold-review-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    workspace.mkdir()
    private=Path(os.environ['TEMP'])/workspace.name;private.mkdir()
    save(OUT/'run-context.json',{'source_sha':source,'workspace':str(workspace),'private_logs':str(private),'started_at':now()})
    env=os.environ.copy();env['PYTHONUTF8']='1'
    prep_log=(OUT/'excel-prepare.txt').open('w',encoding='utf-8')
    p1root=workspace/'p1'
    helper=subprocess.Popen([sys.executable,str(ROOT/'scripts/prepare-p1.py'),str(p1root)],cwd=ROOT,stdout=prep_log,stderr=subprocess.STDOUT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        print('Preparing fresh P0 and owned Excel workbooks',flush=True)
        prepare_work(workspace/'p0')
        run_agent('p0',workspace/'p0',source,'이 프로젝트 requirements.txt의 패키지를 설치해줘.',private)
        deadline=time.monotonic()+120
        while not (p1root/'ready.json').exists() and helper.poll() is None and time.monotonic()<deadline:time.sleep(1)
        if not (p1root/'ready.json').exists():raise RuntimeError('Excel preparation not ready; see excel-prepare.txt')
        for name,sub in [('p1-cold-1','cold'),('p1-cold-2','warm')]:
            work=p1root/sub;file=next(work.glob('*.xlsx'))
            run_agent(name,work,source,file.name+'를 읽고 다음달 예상 생산량을 포함한 추세선을 보여줘.',private)
    finally:
        if p1root.exists():(p1root/'STOP').touch()
        try: helper.wait(timeout=45)
        except subprocess.TimeoutExpired: print('Owned preparation cleanup still pending; do not kill unrelated Excel',flush=True)
        prep_log.close()
    print('All requested fresh Agent runs finished',flush=True)

if __name__=='__main__':main()
