import sys, json, tempfile, subprocess, hashlib
from pathlib import Path
ROOT=Path.cwd();sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from tests.prepare_p0_work import prepare_work
from org_demo import connect_work
from skillloop import cli, envharness_p1
from skillloop.store import SkillStore
from skillloop.usage import UsageTracker
from skillloop.match import FailureObservation, search
out=ROOT/'result/operator-org-cold-20260909'
work=Path(tempfile.mkdtemp(prefix='skillloop-org-preflight-parent-'))/'different-work-path'
ctx=prepare_work(work,seed_local=False)
receipt=connect_work(work,'https://github.com/THEGREATCJPark/ddthon.git','team-skill-demo-20260909')
ctx=json.loads((work/'skillloop-work.json').read_text(encoding='utf-8'))
d=SkillStore(ctx['store']).list()[0]
checks={'remote_p0_only':len(SkillStore(ctx['store']).list())==1 and d.procedure['action']=='pip-install','remote_revision':receipt['commit']}
args=[ctx['requirements'],ctx['work_python'],ctx['store'],ctx['usage'],'preflight-independent-1',ctx['policy']]
checks['unconfirmed_denied']=cli.apply_requirements(*args)==2
checks['unconfirmed_zero_events']=len(UsageTracker(ctx['usage']).list_shared_events())==0
checks['confirmed_real_apply']=cli.apply_requirements(*args,confirmed_digest=d.digest)==0
checks['one_event']=len(UsageTracker(ctx['usage']).list_shared_events())==1
checks['repeat_no_addition']=cli.apply_requirements(*args,confirmed_digest=d.digest)==0 and len(UsageTracker(ctx['usage']).list_shared_events())==1
probe=subprocess.run([ctx['work_python'],'-c','import skillloop_demo_pkg; import importlib.metadata as m; assert m.version("skillloop-demo-pkg")=="1.0.0"'],capture_output=True)
checks['independent_import_version']=probe.returncode==0
p1root=Path(r'C:\Users\cik61\Desktop\skillloop-org-p1-20260909')
for name in ['cold','warm']:
    p1work=p1root/name; file=next(p1work.glob('*.xlsx'))
    h=hashlib.sha256(file.read_bytes()).hexdigest()
    p1ctx=json.loads((p1work/'skillloop-work.json').read_text(encoding='utf-8'))
    store=SkillStore(p1ctx['store'])
    obs=envharness_p1.attempt_direct_access(str(file))
    found=search(FailureObservation('read xlsx','xlsx','file-access-fail:xlsx',1),store)
    # Readiness/adapter check only: no Agent discovery, task, candidate or review performed.
    access=envharness_p1.run_file_access_procedure({'action':'file-access','method':'excel-com-attach'},envharness_p1.EnvContext(str(file),True))
    checks[name]={'direct_failed':obs.ran and not obs.ok,'team_search':found.status,'existing_p0':len(store.list())==1,'exact_excel_readiness':access.ok,'original_unchanged':h==hashlib.sha256(file.read_bytes()).hexdigest(),'candidate_created':False}
checks['live_p0_events']=len(UsageTracker(r'C:\Users\cik61\Desktop\skillloop-org-p0-20260909\.skillloop\usage.json').list_shared_events())
checks['scope']='Automated operator preflight; isolated P0 work. No usage pushed, no P1 candidate/publication, no Agent dialogue claim.'
(out/'organization-preflight.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
