"""Check actual tool output/state; wording flags are review cues, not verdicts."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from skillloop.descriptor import compute_digest

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    global OUT
    if len(sys.argv)>1:OUT=Path(sys.argv[1]).resolve()
    summary={'verified_at':datetime.now(timezone.utc).isoformat(),'runs':[]}
    for name in ('p0','p1-cold-1','p1-cold-2'):
        state=load(OUT/(name+'-status.json'))
        if 'exit_code' not in state:raise RuntimeError(name+' still running')
        events=load(OUT/(name+'-trace.json'));reports=[];texts=[];tool_text=[];errors=[];tools=[]
        for e in events:
            msg=e.get('message',{})
            if not isinstance(msg,dict):continue
            for b in msg.get('content',[]):
                if not isinstance(b,dict):continue
                if e.get('type')=='assistant' and b.get('type')=='text':texts.append(b.get('text',''))
                if b.get('type')=='tool_use':tools.append({'name':b.get('name'),'input':b.get('input')})
                if b.get('type')!='tool_result' or not isinstance(b.get('content'),str):continue
                text=b['content'];tool_text.append(text)
                if b.get('is_error'):errors.append(text)
                for i,ch in enumerate(text):
                    if ch!='{':continue
                    try:r,_=json.JSONDecoder().raw_decode(text[i:])
                    except ValueError:continue
                    if isinstance(r,dict) and 'status' in r and ('trace' in r or 'work' in r):reports.append(r);break
        save(OUT/(name+'-product-reports.json'),reports)
        (OUT/(name+'-responses.md')).write_text('\n\n---\n\n'.join(texts),encoding='utf-8')
        checks={'agent_exit_zero':state['exit_code']==0,'original_unchanged':state['original_unchanged']}
        if name=='p0':
            observed='\n'.join(tool_text)
            checks.update(independent_import=state['independent_import']['exit_code']==0 and state['independent_import']['stdout'].strip()=='1.0.0',
                          reuse_one=sum(state['usage']['counts'].values())==1 and len(state['usage']['events'])==1,
                          store_unchanged=state['store']==state['pre_store'],
                          actual_supply_failure='install exit=1' in observed and 'No matching distribution found' in observed,
                          matched='selected=fix-skillloop-demo-pkg-install' in observed,
                          same_work_environment='WORK_ENV_PRESERVED' in observed)
        else:
            complete=[r for r in reports if r['status']=='WORK_COMPLETE'];r=complete[-1] if complete else {}
            values=[1200,1350,1500] if name.endswith('1') else [2100,2250,2400]
            candidates=[d for d in state['store']['skills'].values() if d['procedure'].get('action')=='file-access']
            checks.update(one_complete=len(complete)==1,values=[x['value'] for x in r.get('work',{}).get('actual',[])]==values,
                          forecast=r.get('work',{}).get('forecast',{}).get('value')==values[-1]+150,
                          forecast_month=r.get('work',{}).get('forecast',{}).get('month')=='2026-08',
                          verified=r.get('work_verified') is True,
                          cold_no_preexisting_skill=all(d['procedure'].get('action')!='file-access' for d in state['pre_store']['skills'].values()),
                          discovery=any(x['status']=='NEEDS_AGENT_DISCOVERY' for x in reports),
                          actual_no_match=any(t.get('step')=='search' and t.get('status')=='NO_MATCH' for t in r.get('trace',[])),
                          direct_failure=any(t.get('step')=='direct-access' and t.get('ran') and 'BadZipFile' in t.get('error','') for t in r.get('trace',[])),
                          candidate_one=r.get('candidate_delta')==1 and len(candidates)==1,
                          reuse_zero=r.get('reuse_delta')==0 and not state['usage']['events'],
                          environment_only=all(d['procedure']=={'action':'file-access','method':'excel-com-attach'} for d in candidates),
                          digest_valid=all(d['digest']==compute_digest({k:d[k] for k in ('id','version','origin','applicability','procedure')}) for d in candidates),
                          no_approval_or_publication=all(x.get('state')=='PROPOSED' and not x.get('local_review_evidence') and not x.get('remote_publish_evidence') for x in state['store'].get('lifecycle',{}).values()),
                          actual_chart=len(state['charts'])==1)
        wording='\n'.join(texts)
        categories={'expected_workflow_pause':sum('NEEDS_AGENT_DISCOVERY' in x or 'NEEDS_TASK_MAPPING' in x for x in errors),
                    'permission_denial':sum('Permission to use' in x for x in errors),
                    'input_schema_or_mapping':sum('run-p1: ERROR' in x for x in errors),
                    'expected_pip_failure':sum('No matching distribution found' in x for x in errors) if name=='p0' else 0}
        categories['other']=len(errors)-sum(categories.values())
        summary['runs'].append({'name':name,'functional':'PASS' if all(checks.values()) else 'FAIL','checks':checks,
                               'intermediate_tool_errors':len(errors),'user_visible_messages':len(texts),
                               'tool_error_categories':categories,
                               'product_environment_label_present':'사내환경 · NASCA(가상)' in '\n'.join(tool_text),
                               'wording_review_markers':{key:wording.count(key) for key in ['사내환경','사내 환경','NASCA(가상)','제품 CLI','합성','harness','supported scope','NOT_RUN','read-only']},
                               'started_at':state['started_at'],'finished_at':state['finished_at'],'source_sha':state['source_sha']})
    save(OUT/'validation.json',summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if any(x['functional']!='PASS' for x in summary['runs']):raise SystemExit(1)

if __name__=='__main__':main()
