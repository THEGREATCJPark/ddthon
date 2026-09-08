"""Derive acceptance findings from actual CLI tool results and operator-side oracles."""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'result/p1-acceptance'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'verified_at':datetime.now(timezone.utc).isoformat(),'runs':[]}
for name in ('warm','cold-1','cold-2','cold-3'):
 state=load(OUT/(name+'-status.json'))
 if 'exit_code' not in state: raise RuntimeError(name+' is still running')
 reports=[];errors=[]
 for event in load(OUT/(name+'-trace.json')):
  if not isinstance(event,dict) or not isinstance(event.get('message'),dict):continue
  content=event['message'].get('content',[])
  for block in content if isinstance(content,list) else []:
   if not isinstance(block,dict):continue
   text=block.get('content')
   if block.get('type')!='tool_result' or not isinstance(text,str):continue
   if block.get('is_error') or 'run-p1: ERROR' in text:errors.append(text)
   for i,ch in enumerate(text):
    if ch!='{':continue
    try:report,end=json.JSONDecoder().raw_decode(text[i:])
    except ValueError:continue
    if isinstance(report,dict) and 'status' in report and ('trace' in report or 'work' in report):reports.append(report);break
 dump(OUT/(name+'-product-reports.json'),reports)
 complete=[r for r in reports if r['status']=='WORK_COMPLETE']
 checks={'agent_exit_zero':state['exit_code']==0,'one_completed_report':len(complete)==1,'original_unchanged':state['original_unchanged'],'chart_created':len(state['charts'])==1}
 result=complete[-1] if complete else {}
 expected=[2100,2250,2400] if name=='warm' else load(OUT/(name+'-operator-profile.json'))['values']
 forecast=max(0,sum(expected)/3+(expected[2]-expected[0]))
 checks.update(actual_values=[r['value'] for r in result.get('work',{}).get('actual',[])]==expected,forecast=result.get('work',{}).get('forecast',{}).get('value')==forecast,forecast_month=result.get('work',{}).get('forecast',{}).get('month')=='2026-08',work_verified=result.get('work_verified') is True)
 warm=name=='warm'
 checks['search']=any(t.get('step')=='search' and t.get('status')==('MATCH' if warm else 'NO_MATCH') for t in result.get('trace',[]))
 checks['direct_failure']=any(t.get('step')=='direct-access' and t.get('ran') is True and t.get('ok') is False and 'BadZipFile' in t.get('error','') for t in result.get('trace',[]))
 checks['candidate_delta']=result.get('candidate_delta')==(0 if warm else 1)
 checks['reuse']=result.get('reused') is warm and (result.get('counted') is True and result.get('reuse')==1 if warm else result.get('reuse_delta')==0)
 checks['event_count']=len(state['usage']['events'])==(1 if warm else 0)
 if not warm:
  checks['discovery_gate']=any(r['status']=='NEEDS_AGENT_DISCOVERY' for r in reports)
  checks['cold_store_no_excel_skill']=len(state['pre_store']['skills'])==1 and all('file-access' not in str(d) for d in state['pre_store']['skills'].values())
  candidate=[d for d in state['store']['skills'].values() if d['id'].startswith('file-access-')][0]
  checks['task_independent_candidate']=candidate['procedure']=={'action':'file-access','method':'excel-com-attach'} and candidate['digest']=='359c5c1763416cdb3aa9828adef40219d1ac5448f82d62f91ebbca82768727af'
 summary['runs'].append({'name':name,'verdict':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'forecast':forecast,'values':expected,'intermediate_error_count':len(errors),'started_at':state['started_at'],'finished_at':state['finished_at'],'source_sha':state['source_sha'],'charts':state['charts']})
summary['all_pass']=all(r['verdict']=='PASS' for r in summary['runs'])
summary['limitations']=['Same Windows PC; independent workspaces/sessions and actual GitHub remote, not B-PC validation.','Warm Agent final narrative incorrectly attributed failure to file lock; actual direct-reader evidence is BadZipFile on Office-encrypted bytes.','Some agent tool/schema attempts failed before recovery; preserved in traces, not flawless first-try execution.','Terminal status popularity/count remain local; organization events are available in the shared snapshot.','S3/database adapter not implemented.']
dump(OUT/'validation.json',summary)
print(json.dumps(summary,ensure_ascii=True,indent=2))
if not summary['all_pass']:raise SystemExit(1)
