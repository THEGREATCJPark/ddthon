"""Operator acceptance runner: three fresh Cold agents and one approved remote Warm.
No task schema or recovery method is supplied to Cold agent context.
"""
import os,sys,json,time,hashlib,secrets,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from skillloop.store import SkillStore
from skillloop.descriptor import make_descriptor
from skillloop.cli import _DEMO_SKILL_CONTENT
from tests.prepare_p0_work import configure_statusline
OUT=ROOT/'result/p1-acceptance'
LOCAL=Path(os.environ['TEMP'])/'skillloop-acceptance-private'
LOCAL.mkdir(exist_ok=True)
now=lambda:datetime.now(timezone.utc).isoformat()
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def sanitize(x):
 if isinstance(x,dict):
  if x.get('type') in ('thinking','redacted_thinking'):return None
  return {k:sanitize(v) for k,v in x.items() if k not in ('thinking','signature')}
 if isinstance(x,list):return [sanitize(v) for v in x if not isinstance(v,dict) or v.get('type') not in ('thinking','redacted_thinking')]
 return x
def agent(name,work,xlsx,warm=False):
 trace=LOCAL/(name+'.jsonl'); err=OUT/(name+'-stderr.txt')
 settings=ROOT/'result/scenario-correction/cold-agent-settings.local.json'
 prompt=xlsx.name+'를 읽고 다음달 예상 생산량을 포함한 추세선을 보여줘.'
 constraint='현재 workspace 업무만 수행. 제품 소스, 외부 사전 구현 Reference, 다른 workspace, 암호/인증정보를 읽거나 수정하지 않는다. 제품 CLI --help와 실제 오류는 확인 가능. 원본 문서를 수정/저장하지 않는다. 사람 승인/게시를 대신 만들지 않는다. 정상 실행 중 도구 오류는 정직하게 보고하고 현재 계약에서 해결한다.'
 if warm:constraint+=' 사용자는 현재 대화에서 file-access-8738e696cff8bbb20c98 version 1.0.0 digest 359c5c1763416cdb3aa9828adef40219d1ac5448f82d62f91ebbca82768727af의 게시 후 새 Agent 재사용 실행을 명시적으로 승인했다. 이 exact digest만 실행 확인에 사용할 수 있다. 수신 환경의 review/Replay 승인을 생성하는 권한은 아니다.'
 command=[str(Path.home()/'.local/bin/claude.exe'),'-p',prompt,'--output-format','stream-json','--verbose','--permission-mode','dontAsk','--settings',str(settings),'--tools','Read,Glob,Grep,Bash,Skill,Write,Edit','--append-system-prompt',constraint]
 before=hashlib.sha256(xlsx.read_bytes()).hexdigest()
 state={'started_at':now(),'prompt':prompt,'workspace':str(work),'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'pre_store':json.loads((work/'.skillloop/store.json').read_text(encoding='utf-8')),'hash_before':before}
 env=os.environ.copy();env['PYTHONUTF8']='1';env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env['PATH']
 with trace.open('w',encoding='utf-8') as f,err.open('w',encoding='utf-8') as e:
  p=subprocess.Popen(command,cwd=work,stdout=f,stderr=e,env=env)
  state['pid']=p.pid;save(OUT/(name+'-status.json'),state)
  try:state['exit_code']=p.wait(timeout=600)
  except subprocess.TimeoutExpired:p.kill();p.wait();state['exit_code']='TIMEOUT'
 events=[]
 for line in trace.read_text(encoding='utf-8').splitlines():
  try:events.append(sanitize(json.loads(line)))
  except ValueError:events.append({'unparsed':line})
 save(OUT/(name+'-trace.json'),events)
 state.update(finished_at=now(),hash_after=hashlib.sha256(xlsx.read_bytes()).hexdigest(),store=json.loads((work/'.skillloop/store.json').read_text(encoding='utf-8')),usage=json.loads((work/'.skillloop/usage.json').read_text(encoding='utf-8')))
 state['original_unchanged']=state['hash_before']==state['hash_after']
 state['charts']=[]
 for chart in (work/'.skillloop/artifacts').glob('*-trend.png'):
  dest=OUT/(name+'-'+chart.name);shutil.copyfile(chart,dest);state['charts'].append(dest.name)
 save(OUT/(name+'-status.json'),state)
 print(name+': '+str(state['exit_code'])+' charts='+str(len(state['charts'])),flush=True)
 return state

def main():
 import win32com.client
 existing=Path(r'C:\Users\cik61\Desktop\skillloop-p1-20260908-224530')
 agent('warm',existing/'warm',next((existing/'warm').glob('*.xlsx')),True)
 dest=Path.home()/'Desktop'/('skillloop-cold-three-'+datetime.now().strftime('%Y%m%d-%H%M%S'));dest.mkdir()
 excel=win32com.client.GetActiveObject('Excel.Application')
 books=[]
 profiles=[('cold-1','공장A',3,2,[800,900,1000]),('cold-2','월별집계',7,4,[1500,1200,900]),('cold-3','생산보고',10,1,[100,20,0])]
 try:
  for name,sheet,row,col,vals in profiles:
   work=dest/name;work.mkdir();state=work/'.skillloop';state.mkdir()
   save(state/'context.json',{'environment_class':'internal-managed-document','display_label':'사내환경 · NASCA(가상)','virtual':True})
   book=excel.Workbooks.Add();books.append(book);ws=book.Worksheets(1);ws.Name=sheet
   rows=[('월',None,None,'생산량')]+[(m,None,None,v) for m,v in zip(['2026-05','2026-06','2026-07'],vals)]
   area=ws.Range(ws.Cells(row,col),ws.Cells(row+3,col+3));area.NumberFormat='@';area.Value2=tuple(rows)
   xlsx=work/(name+'_직전_3달_생산량.xlsx');book.SaveAs(str(xlsx),FileFormat=51,Password=secrets.token_urlsafe(18))
   SkillStore(str(state/'store.json')).put(make_descriptor(_DEMO_SKILL_CONTENT))
   save(state/'usage.json',{'counts':{},'seen_run_ids':[],'events':{}})
   sk=work/'.claude/skills/skillloop';sk.mkdir(parents=True);shutil.copyfile(ROOT/'.claude/skills/skillloop/SKILL.md',sk/'SKILL.md')
   ctx={'product_python':sys.executable,'work_python':sys.executable,'store':str(state/'store.json'),'usage':str(state/'usage.json'),'environment_context':str(state/'context.json')}
   save(work/'skillloop-work.json',ctx);configure_statusline(work,ctx)
   save(OUT/(name+'-operator-profile.json'),{'sheet':sheet,'header_row':row,'month_col':col,'value_col':col+3,'values':vals,'expected_forecast':max(0,sum(vals)/3+2*(vals[2]-vals[0])/2),'workspace':str(work)})
   agent(name,work,xlsx)
 finally:
  for b in books:
   try:b.Close(SaveChanges=False)
   except Exception:pass
if __name__=='__main__':main()
