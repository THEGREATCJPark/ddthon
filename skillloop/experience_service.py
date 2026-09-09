"""S2: observed P1 failure, Agent-supplied alternative, task verification, candidate.

No environment creation, automatic alternative choice, approval or publication here.
"""
import ast
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

from . import envharness_p1 as harness, match, reuse_service
from .descriptor import make_descriptor, compute_digest
from .publish_pipeline import PublishPipeline, exact_ref
from .store import SkillStore
from .usage import UsageTracker, build_evidence, new_execution_id

SIGNAL = 'file-access-fail:xlsx'


def compute_ols_forecast(content):
    if not isinstance(content, (list, tuple)) or len(content) < 3:
        raise ValueError('Three completed months required')
    rows = []
    for row in content:
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise ValueError('Invalid work row')
        month, value = row
        if not isinstance(month, str) or datetime.strptime(month, '%Y-%m').strftime('%Y-%m') != month:
            raise ValueError('Invalid month')
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError('Invalid total output')
        rows.append((month, value))
    if len({m for m, _ in rows}) != len(rows):
        raise ValueError('Duplicate completed month')
    rows = sorted(rows)[-3:]
    year, month = map(int, rows[-1][0].split('-'))
    next_month = f'{year + (month == 12):04d}-{month % 12 + 1:02d}'
    values = [v for _, v in rows]
    slope = (values[2] - values[0]) / 2
    forecast = max(0, sum(values) / 3 + 2 * slope)
    return {'kind': 'WORK_RESULT', 'actual': [{'month': m, 'value': v, 'type': 'actual'} for m, v in rows],
            'forecast': {'month': next_month, 'value': forecast, 'type': 'forecast'},
            'unit': 'total_output', 'method': '3-point OLS, x=1..3 -> x=4, clamp=0'}


def verify_work_result(result, content):
    return result == compute_ols_forecast(content)


def candidate_procedure(procedure):
    if procedure != {'action': 'file-access', 'method': 'excel-com-attach'}:
        raise ValueError('Unsupported discovered procedure. This adapter accepts exactly '
                         '{"action":"file-access","method":"excel-com-attach"}; '
                         'use only if that matches the approach you actually discovered. Task schema stays local.')
    return dict(procedure)


def task_rows(snapshot, mapping):
    """Agent supplies task-specific mapping after inspecting the local snapshot."""
    if not harness._valid_snapshot(snapshot):
        raise ValueError('Invalid workbook snapshot')
    if not isinstance(mapping, dict) or set(mapping) != {'sheet', 'month_col', 'total_col', 'first_row'}:
        raise ValueError('Explicit local sheet/month_col/total_col/first_row mapping required')
    if any(type(mapping[k]) is not int or mapping[k] < 1 for k in ('month_col', 'total_col', 'first_row')):
        raise ValueError('Positive task coordinates required')
    if mapping['month_col'] == mapping['total_col']:
        raise ValueError('Month and total columns must differ')
    sheets = [sheet for sheet in snapshot['sheets'] if sheet['name'] == mapping['sheet']]
    if len(sheets) != 1:
        raise ValueError('Explicit sheet name not found uniquely')
    sheet = sheets[0]; rows = []
    mc, vc = mapping['month_col'] - sheet['first_col'], mapping['total_col'] - sheet['first_col']
    if min(mc, vc) < 0 or max(mc, vc) >= len(sheet['values'][0]):
        raise ValueError('Task columns outside observed used range')
    for offset, values in enumerate(sheet['values']):
        if sheet['first_row'] + offset < mapping['first_row']:
            continue
        month, value = values[mc], values[vc]
        if month is None and value is None:
            continue
        rows.append((month, value))
    compute_ols_forecast(rows)  # actual validation, never silently coerce invalid task rows
    return rows


def write_chart(work, destination):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    path = Path(destination); path.parent.mkdir(parents=True, exist_ok=True)
    fig = Figure(figsize=(8, 4), layout='constrained'); FigureCanvasAgg(fig)
    ax = fig.subplots()
    actual = work['actual']; forecast = work['forecast']
    ax.plot(range(3), [r['value'] for r in actual], 'o-', label='Actual')
    ax.plot([2, 3], [actual[-1]['value'], forecast['value']], 'o--', label='Forecast (OLS)')
    ax.set_xticks(range(4), [r['month'] for r in actual] + [forecast['month']])
    ax.set_ylabel('Total output'); ax.set_title('Production: 3 actual months + 1 forecast')
    ax.legend(); ax.grid(alpha=.25)
    fig.savefig(path, dpi=150)
    return str(path.resolve())


def finish_task(snapshot, mapping, store_path, run_id):
    # These local artifacts are never included in descriptor or shared events.
    folder = Path(store_path).parent / 'artifacts'; folder.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(run_id.encode()).hexdigest()[:20]
    artifact = folder / (key + '-workbook.json')
    artifact.write_text(json.dumps(snapshot, ensure_ascii=False), encoding='utf-8')
    if mapping is None:
        return {'status': 'NEEDS_TASK_MAPPING', 'artifact_ref': str(artifact.resolve())}
    content = task_rows(snapshot, mapping)
    work = compute_ols_forecast(content)
    return {'status': 'WORK_COMPLETE', 'work': work, 'work_verified': verify_work_result(work, content),
            'chart_ref': write_chart(work, folder / (key + '-trend.png'))}


def build_candidate(procedure, author='local'):
    procedure = candidate_procedure(procedure)
    fingerprint = hashlib.sha256(json.dumps(procedure, sort_keys=True).encode()).hexdigest()[:20]
    return make_descriptor({'id': 'file-access-' + fingerprint, 'version': '1.0.0',
                            'origin': {'author': author}, 'applicability': {'signals': [SIGNAL]},
                            'procedure': procedure})


def execute_p1(xlsx_path, store, usage, run_id, *, app_open=False, procedure=None,
               confirmed_digest=None, author='local', task_mapping=None):
    observation = harness.attempt_direct_access(xlsx_path)
    if not observation.ran:
        return {'status': 'NOT_RUN', 'reason': observation.error}
    if observation.ok:
        return {'status': 'DIRECT_ACCESS_OK', 'reason': 'No failed access requiring Skill recovery', 'reuse_delta': 0}
    if not (observation.error or '').startswith('BadZipFile:'):
        return {'status': 'ACCESS_ERROR', 'reason': observation.error}
    obs = match.FailureObservation('read xlsx', 'xlsx', SIGNAL, 1)
    outcome = match.search(obs, store)
    trace = [{'step': 'direct-access', 'ran': observation.ran, 'ok': observation.ok, 'error': observation.error},
             {'step': 'search', 'scope': 'Team Skill', 'query': SIGNAL,
              'org_knowledge': {'status': 'not_provided', 'searched': False},
              'status': outcome.status, 'rationale': outcome.rationale}]
    env = harness.EnvContext(xlsx_path, app_open)
    if outcome.status == 'MATCH':
        selected = outcome.descriptor
        if compute_digest(vars(selected)) != selected.digest:
            return {'status': 'INTEGRITY_ERROR', 'trace': trace, 'reuse_delta': 0}
        if not PublishPipeline(store).reuse_eligible(selected):
            return {'status': 'REVIEW_REQUIRED', 'selected': exact_ref(selected), 'trace': trace, 'reuse_delta': 0}
        if confirmed_digest != selected.digest:
            return {'status': 'CONFIRMATION_REQUIRED', 'selected': exact_ref(selected), 'trace': trace}
        candidate_procedure(selected.procedure)
        result = reuse_service.apply_and_verify(selected, obs, env, run_id)
        if not result.is_real_success:
            return {'status': 'NOT_RUN' if result.access_method == 'none' else 'FAIL', 'trace': trace}
        # A's existing artifact is a Python literal representation, never executable code.
        content = ast.literal_eval(Path(result.artifact_ref).read_text(encoding='utf-8'))
        task = finish_task(content, task_mapping, store.path, run_id)
        if task['status'] != 'WORK_COMPLETE':
            return {**task, 'trace': trace, 'candidate_delta': 0}
        verified = {'is_real_success': True, 'action': 'file-access',
                    'original_unchanged': result.access_evidence.get('original_unchanged'),
                    'save_called': result.access_evidence.get('save_called')}
        rec = usage.record_actual_reuse(build_evidence(exact_ref(selected), verified, run_id,
                                                       demo_seed=selected.demo_seed, reuser_alias=author))
        return {**task, 'reused': True, 'counted': rec.counted, 'reuse': rec.new_count,
                'candidate_delta': 0, 'trace': trace}
    if outcome.status != 'NO_MATCH':
        return {'status': outcome.status, 'trace': trace}
    if procedure is None:
        return {'status': 'NEEDS_AGENT_DISCOVERY', 'trace': trace,
                'facts_needed': '직접 읽기 실패와 팀 Skill 검색 결과만 알리고, '
                                '사용자가 환경 사실을 이어서 제공할 때까지 기다립니다. '
                                '이미 대화에서 제공된 사실은 재질문하지 않습니다.'}
    procedure = candidate_procedure(procedure)  # never choose or default the solution
    access = harness.run_file_access_procedure(procedure, env)
    if not access.ok:
        return {'status': 'NOT_RUN' if access.method == 'none' else 'FAIL', 'trace': trace}
    task = finish_task(access.content, task_mapping, store.path, run_id)
    if task['status'] != 'WORK_COMPLETE':
        return {**task, 'trace': trace, 'candidate_delta': 0}
    candidate = build_candidate(procedure, author)
    previous = store.get(candidate.id, candidate.version)
    PublishPipeline(store).propose(candidate)
    return {**task, 'reused': False, 'reuse_delta': 0,
            'candidate_delta': 0 if previous else 1, 'candidate': exact_ref(candidate),
            'next_action': {'type': 'REQUEST_HUMAN_PUBLICATION_REVIEW',
                            'candidate_ref': exact_ref(candidate),
                            'message': '이 해결 방법을 팀 Skill로 공유할까요? 승인 후 독립 재검증을 거쳐 게시합니다.'},
            'trace': trace}


def run_p1(xlsx_path=None, store_path=None, usage_path=None, run_id=None, **kwargs):
    if not xlsx_path:
        print('run-p1: NOT_RUN — explicit work XLSX required')
        return 2
    base = Path.cwd() / '.skillloop'
    context_file = Path(store_path).parent / 'context.json' if store_path else base / 'context.json'
    if context_file.is_file():
        try:
            context = json.loads(context_file.read_text(encoding='utf-8'))
            if context.get('virtual') is True and context.get('environment_class') == 'internal-managed-document':
                label = ('NASCA 보안 프로그램' if context.get('scenario_id') == 'hackathon-nasca'
                         else '사내환경 · NASCA(가상)')
                print(f'작업 환경: {label}')
        except (OSError, ValueError):
            pass  # descriptive context is not an execution/approval gate
    try:
        report = execute_p1(str(Path(xlsx_path).resolve()), SkillStore(str(store_path or base / 'store.json')),
                            UsageTracker(str(usage_path or base / 'usage.json')), run_id or new_execution_id(), **kwargs)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report['status'] == 'WORK_COMPLETE' else 2
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        print(f'run-p1: ERROR {exc}')
        return 2
