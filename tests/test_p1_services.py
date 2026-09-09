from tests.p1_helpers import snapshot, PROC, MAPPING
import copy
import json
import subprocess
from types import SimpleNamespace

import pytest
from hypothesis import given, strategies as st

from skillloop import envharness_p1 as h
from skillloop.experience_service import build_candidate, compute_ols_forecast, execute_p1
from skillloop.publish_pipeline import PublishPipeline, exact_ref
from skillloop.gitsync import GitSyncAdapter
from skillloop.store import SkillStore
from skillloop.usage import UsageTracker, build_evidence

ROWS = [('2026-05', 1200), ('2026-06', 1350), ('2026-07', 1500)]
PROC = dict(PROC)


@given(st.integers(min_value=0, max_value=10000), st.integers(min_value=0, max_value=1000))
def test_linear_forecast_property(base, step):
    rows = [('2026-10', base), ('2026-11', base + step), ('2026-12', base + 2 * step)]
    result = compute_ols_forecast(rows)
    assert result['forecast']['month'] == '2027-01'
    assert result['forecast']['value'] == pytest.approx(base + 3 * step)


def test_forecast_contract_and_bad_input():
    assert compute_ols_forecast(ROWS)['forecast'] == {'month': '2026-08', 'value': 1650, 'type': 'forecast'}
    assert compute_ols_forecast([('2026-01', 100), ('2026-02', 0), ('2026-03', 0)])['forecast']['value'] == 0
    for rows in [[('2026-01', True)] * 3, [('2026-01', float('nan'))] * 3, ROWS[:2], [ROWS[0]] * 3]:
        with pytest.raises(ValueError): compute_ols_forecast(rows)


def test_candidate_excludes_data_and_password():
    for field in ('password', 'content', 'formula', 'xlsx_path', 'script'):
        with pytest.raises(ValueError): build_candidate({**PROC, field: 'forbidden'})
    assert build_candidate(PROC).digest == build_candidate(dict(PROC)).digest


@pytest.fixture
def scope(tmp_path, monkeypatch):
    file = tmp_path / 'work.xlsx'
    file.write_bytes(h._OLE_CFB_MAGIC + b'unit-test-placeholder')
    monkeypatch.setattr(h, '_read_via_excel_attach', lambda *a: snapshot(ROWS))
    return file, SkillStore(str(tmp_path / 'store.json')), UsageTracker(str(tmp_path / 'usage.json'))


def test_discovery_is_not_auto_selected_and_warm_counts(scope):
    file, store, usage = scope
    cold = execute_p1(str(file), store, usage, 'cold', app_open=True)
    assert cold['status'] == 'NEEDS_AGENT_DISCOVERY'
    assert store.list() == []
    created = execute_p1(str(file), store, usage, 'cold', app_open=True, procedure=PROC, task_mapping=MAPPING)
    assert created['candidate_delta'] == 1 and not created['reused']
    d = store.list()[0]
    denied = execute_p1(str(file), store, usage, 'warm', app_open=True)
    assert denied['status'] == 'REVIEW_REQUIRED'
    pipeline = PublishPipeline(store)
    pipeline.review(d, 'approve', 'test-reviewer')
    pipeline.replay(d, h.EnvContext(str(file), True))
    warm = execute_p1(str(file), store, usage, 'warm', app_open=True, confirmed_digest=d.digest, task_mapping=MAPPING)
    assert warm['status'] == 'WORK_COMPLETE' and warm['work_verified']
    assert warm['candidate_delta'] == 0 and warm['counted']
    retry = execute_p1(str(file), store, usage, 'warm', app_open=True, confirmed_digest=d.digest, task_mapping=MAPPING)
    assert not retry['counted'] and retry['reuse'] == 1
    assert str(file) not in json.dumps(usage.list_shared_events())
    assert '1200' not in json.dumps(usage.list_shared_events())


def test_cold_fact_wait_records_actual_scope_without_access_or_state_writes(scope, monkeypatch):
    file, store, usage = scope
    def forbidden(*args, **kwargs):
        raise AssertionError('No discovered procedure: must not access the application')
    monkeypatch.setattr(h, 'run_file_access_procedure', forbidden)
    report = execute_p1(str(file), store, usage, 'waiting-for-user')
    assert report['status'] == 'NEEDS_AGENT_DISCOVERY'
    observed, search = report['trace']
    assert observed['ran'] and not observed['ok']
    assert search['status'] == 'NO_MATCH'
    assert search['scope'] == 'Team Skill' and search['query'] == 'file-access-fail:xlsx'
    assert search['org_knowledge'] == {'status': 'not_provided', 'searched': False}
    assert store.list() == [] and usage.list_shared_events() == []


def test_review_replay_gate_restart_and_mutation(scope):
    file, store, usage = scope
    d = build_candidate(PROC)
    pipeline = PublishPipeline(store); pipeline.propose(d)
    transport = SimpleNamespace(push_descriptors=lambda b: {'ok': True, 'commit': 'test-commit', 'branch': 'team-skill-store'})
    assert pipeline.publish(d, transport)['state'] == 'BLOCKED'
    pipeline.review(d, 'reject', 'reviewer')
    assert pipeline.publish(d, transport)['state'] == 'BLOCKED'
    pipeline.review(d, 'approve', 'reviewer')
    assert pipeline.publish(d, transport)['state'] == 'BLOCKED'
    assert pipeline.replay(d, h.EnvContext(str(file), False))['state'] == 'BLOCKED'
    assert pipeline.publish(d, transport)['state'] == 'BLOCKED'
    assert pipeline.replay(d, h.EnvContext(str(file), True))['state'] == 'LOCALLY_APPROVED'
    fail = SimpleNamespace(push_descriptors=lambda b: {'ok': False, 'error': 'test transport failure'})
    assert pipeline.publish(d, fail)['state'] == 'PUBLISH_PENDING'
    restarted = PublishPipeline(SkillStore(store.path))
    assert restarted.publish(d, transport)['state'] == 'PUBLISHED'
    modified = copy.deepcopy(d); modified.procedure['sheet'] = 2
    with pytest.raises(ValueError, match='INTEGRITY'): restarted.publish(modified, transport)
    restarted.review(d, 'approve', 'reviewer')
    assert restarted.publish(d, transport)['state'] == 'BLOCKED'  # no inherited Replay


def test_real_git_publish_pull_usage_dedup(scope, tmp_path):
    file, store, usage = scope
    remote = tmp_path / 'remote.git'
    subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
    a, b = GitSyncAdapter(tmp_path / 'mirror-a', remote), GitSyncAdapter(tmp_path / 'mirror-b', remote)
    d = build_candidate(PROC); pipeline = PublishPipeline(store); pipeline.propose(d)
    pipeline.review(d, 'approve', 'unit-test-reviewer')  # explicit test review, not real human evidence
    pipeline.replay(d, h.EnvContext(str(file), True))  # mocked Excel reader, real Git below
    assert pipeline.publish(d, a)['state'] == 'PUBLISHED'
    other = SkillStore(str(tmp_path / 'other.json')); other_usage = UsageTracker(str(tmp_path / 'other-usage.json'))
    result = b.pull(other, other_usage)
    assert result['ok'] and result['imported'] == 1
    record = PublishPipeline(other).query_lifecycle_state(exact_ref(d))
    assert record['remote_publish_evidence']['commit']
    assert record['local_review_evidence'] is None and record['replay'] is None
    assert PublishPipeline(other).publish(d, b)['state'] == 'BLOCKED'
    other_usage.record_actual_reuse(build_evidence(exact_ref(d), {'is_real_success': True}, 'test-use', reuser_alias='B'))
    assert b.push_shared_usage(other_usage.export_shared_usage())['ok']
    assert a.pull(store, usage)['events'] == 1
    assert a.pull(store, usage)['events'] == 0
    assert usage.shared_reuse_count(d.id, d.version) == 1
    assert not any(p.suffix == '.db' for p in (tmp_path / 'mirror-a').rglob('*'))


def test_mirror_refuses_existing_worktree(tmp_path):
    p = tmp_path / 'existing'; p.mkdir(); (p / 'README.md').write_text('keep')
    with pytest.raises(ValueError): GitSyncAdapter(p, 'test-remote').initialize()
    assert (p / 'README.md').read_text() == 'keep'


def test_cli_review_requires_exact_human_confirmation(scope, monkeypatch):
    from skillloop import cli
    file, store, usage = scope
    d = build_candidate(PROC); PublishPipeline(store).propose(d)
    args = ['review', '--store', store.path, '--id', d.id, '--version', d.version,
            '--decision', 'approve', '--reviewer', 'test-human']
    monkeypatch.setattr('builtins.input', lambda _: 'yes')
    assert cli.main(args) == 2
    assert PublishPipeline(SkillStore(store.path)).query_lifecycle_state(exact_ref(d))['local_review_evidence'] is None
    monkeypatch.setattr('builtins.input', lambda _: 'approve ' + d.digest)
    assert cli.main(args) == 0
    assert PublishPipeline(SkillStore(store.path)).query_lifecycle_state(exact_ref(d))['state'] == 'APPROVED'


def test_status_uses_s3_view_without_git_mutation(scope, monkeypatch, capsys):
    from skillloop import cli
    file, store, usage = scope
    d = build_candidate(PROC); PublishPipeline(store).propose(d)
    monkeypatch.setattr(GitSyncAdapter, '_git', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('UI must not run Git')))
    assert cli.cmd_status(store.path, usage.path) == 0
    output = capsys.readouterr().out
    # S3 is connected (candidate exists, no published Skill), while Git sync
    # has never run. These are independent states, not a shared unknown flag.
    assert '게시 상태 확인 대기' not in output
    assert '공개 Skill 0개' in output
    assert '팀 동기화 미연결' in output
    assert '팀 실적 확인 대기' in output
