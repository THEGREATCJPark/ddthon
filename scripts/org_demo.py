"""Operator organization setup helpers; never run as Agent problem recovery."""
import json
import shlex
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skillloop.descriptor import make_descriptor
from skillloop.publish_pipeline import PublishPipeline, exact_ref
from skillloop.store import SkillStore
from skillloop.usage import UsageTracker
from skillloop.gitsync import GitSyncAdapter
from skillloop import envharness_p0
from tests.prepare_p0_work import configure_statusline

P0_CONTENT = {'id': 'fix-skillloop-demo-pkg-install', 'version': '2.0.0',
              'origin': {'author': '박찬준'},
              'applicability': {'signals': ['pip-install-fail']},
              'procedure': {'action': 'pip-install', 'source': 'internal-packages'}}


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def bootstrap(destination, remote, branch):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError('New bootstrap directory required')
    destination.mkdir(parents=True)
    store = SkillStore(str(destination / 'store.json'))
    candidate = make_descriptor(P0_CONTENT)
    PublishPipeline(store).propose(candidate)
    context = {'name': envharness_p0.TARGET_PKG, 'version': envharness_p0.TARGET_VERSION,
               'import_module': envharness_p0.TARGET_IMPORT,
               'sources': {'internal-packages': envharness_p0.resolve_index('allow')}}
    write_json(destination / 'pip-replay-context.json', context)
    write_json(destination / 'sync-config.local.json', {'remote': remote, 'branch': branch,
               'mirror': str(destination / 'mirror')})
    write_json(destination / 'candidate-review.json', {**exact_ref(candidate),
               'content': P0_CONTENT, 'status': 'HUMAN_REVIEW_REQUIRED'})
    return exact_ref(candidate)


def authorize_p0(work):
    """Explicit operator action: authorize only the already-reviewed known P0 content."""
    work = Path(work).resolve()
    context = json.loads((work / 'skillloop-work.json').read_text(encoding='utf-8'))
    store = SkillStore(context['store'])
    expected = make_descriptor(P0_CONTENT)
    candidate = store.get(expected.id, expected.version)
    pipeline = PublishPipeline(store)
    state = pipeline.query_lifecycle_state(exact_ref(expected)) or {}
    if (candidate is None or exact_ref(candidate) != exact_ref(expected)
            or state.get('state') != 'PUBLISHED' or not pipeline.reuse_eligible(candidate)
            or any(pipeline.transport_context.get(k) != context.get(k) for k in ('remote', 'branch'))):
        raise ValueError('Known reviewed P0 must be received from the configured organization first')
    policy_path = Path(context['policy'])
    policy = json.loads(policy_path.read_text(encoding='utf-8'))
    source = Path(policy['sources'][candidate.procedure['source']]).resolve(strict=True)
    if not source.is_dir() or str(source).startswith('\\\\'):
        raise ValueError('Approved local package source required')
    scope = {'mode': 'same-request-p0', 'skills': [exact_ref(candidate)],
             'remote': context['remote'], 'branch': context['branch'],
             'requirements': str(Path(context['requirements']).resolve(strict=True)),
             'work_python': str(Path(context['work_python']).resolve(strict=True)),
             'sources': {candidate.procedure['source']: str(source)}}
    policy['scoped_auto_apply'] = scope
    write_json(policy_path, policy)
    return {'operator_scope': scope, 'data_preserved': True}


def connect_work(work, remote, branch, reviewer='박찬준', *, authorize_request=False,
                 require_p1_absent=True):
    work = Path(work).resolve()
    context_path = work / 'skillloop-work.json'
    context = json.loads(context_path.read_text(encoding='utf-8'))
    state = Path(context['store']).parent
    transport = GitSyncAdapter(state / 'org-mirror', remote, branch)
    transport.initialize()
    config = {'mirror': str(transport.path), **transport.context}
    write_json(state / 'sync-config.local.json', config)
    store, usage = SkillStore(context['store']), UsageTracker(context['usage'])
    receipt = transport.pull(store, usage)
    if not receipt.get('ok'):
        raise RuntimeError('Organization sync failed; inspect receipt and retry')
    if require_p1_absent and any(d.procedure.get('action') == 'file-access' for d in store.list()):
        raise ValueError('P1 already present: not a Cold preparation; data preserved')
    context.update(config, reviewer=reviewer, author=reviewer, organization='디디톤 기술혁신팀')
    context['scope'] = 'Git 동기화 조직 Skill; 원격 절차는 exact 실행 확인 후 사용'
    if context.get('requirements'):
        # Source resolution is local policy, execution approvals are initially empty.
        # Importing a remote descriptor never authorizes its execution by itself.
        policy = {'approved_skills': [], 'sources': {'internal-packages': envharness_p0.resolve_index('allow')},
                  'imports': {envharness_p0.TARGET_PKG: envharness_p0.TARGET_IMPORT}}
        policy_path = state / 'pip-policy.json'
        if not policy_path.exists():
            write_json(policy_path, policy)
        context['policy'] = str(policy_path)
    write_json(context_path, context)
    configure_statusline(work, context)
    settings_path = work / '.claude/settings.local.json'
    settings = json.loads(settings_path.read_text(encoding='utf-8'))
    settings['statusLine']['command'] += ' --alias ' + shlex.quote(reviewer)
    write_json(settings_path, settings)
    write_json(state / 'organization-preparation.json', {'sync': receipt,
                'skills': [exact_ref(d) for d in store.list()],
                'p1_present': any(d.procedure.get('action') == 'file-access' for d in store.list())})
    if authorize_request and context.get('requirements'):
        authorize_p0(work)
    return receipt
