import copy
import json
from types import SimpleNamespace

import pytest
from hypothesis import given, strategies as st

from skillloop import envharness_p1 as h, replay, reuse_service
from skillloop.experience_service import build_candidate, execute_p1, task_rows
from skillloop.publish_pipeline import PublishPipeline
from skillloop.store import SkillStore
from skillloop.usage import UsageTracker
from tests.p1_helpers import PROC, MAPPING, snapshot

ROWS = [('2026-05', 1200), ('2026-06', 1350), ('2026-07', 1500)]


def test_corrupt_digest_rejected_before_execution_or_count(tmp_path, monkeypatch):
    path = tmp_path / 'file.xlsx'; path.write_bytes(b'not-a-zip')
    store = SkillStore(str(tmp_path / 'store.json'))
    d = build_candidate(PROC)
    damaged = copy.deepcopy(d); damaged.procedure['sheet'] = 2
    store.put(damaged)
    usage = UsageTracker(str(tmp_path / 'usage.json'))
    monkeypatch.setattr(reuse_service, 'apply_and_verify', lambda *a: pytest.fail('must not execute'))
    result = execute_p1(str(path), store, usage, 'corrupt', app_open=True, confirmed_digest=d.digest)
    assert result['status'] == 'INTEGRITY_ERROR'
    assert not (tmp_path / 'usage.json').exists()


def test_rejected_cannot_become_reuse_by_digest_confirmation(tmp_path, monkeypatch):
    path = tmp_path / 'file.xlsx'; path.write_bytes(b'not-a-zip')
    store = SkillStore(str(tmp_path / 'store.json')); d = build_candidate(PROC)
    pipeline = PublishPipeline(store); pipeline.propose(d); pipeline.review(d, 'reject', 'test-reviewer')
    monkeypatch.setattr(reuse_service, 'apply_and_verify', lambda *a: pytest.fail('must not execute'))
    result = execute_p1(str(path), store, UsageTracker(str(tmp_path / 'usage.json')), 'rejected',
                        app_open=True, confirmed_digest=d.digest)
    assert result['status'] == 'REVIEW_REQUIRED'
    assert not (tmp_path / 'usage.json').exists()


def test_com_read_exception_is_fail_with_reason(tmp_path, monkeypatch):
    path = tmp_path / 'file.xlsx'; path.write_bytes(b'not-a-zip')
    def fail(*args): raise RuntimeError('workbook enumeration failed')
    monkeypatch.setattr(h, '_read_via_excel_attach', fail)
    result = replay.replay(build_candidate(PROC), h.EnvContext(str(path), True))
    assert result.verdict == 'FAIL'
    assert result.evidence['access_evidence']['ran']
    assert 'enumeration failed' in result.evidence['access_evidence']['error']


def test_reader_preserves_usedrange_origin():
    used = SimpleNamespace(Row=5, Column=3, Rows=SimpleNamespace(Count=3),
                           Columns=SimpleNamespace(Count=2), Value2=ROWS)
    wb = SimpleNamespace(Worksheets=[SimpleNamespace(Name='Different', UsedRange=used)])
    actual = h._snapshot_workbook(wb)
    assert actual == snapshot(ROWS, name='Different', row=5, col=3)
    mapping = {'sheet': 'Different', 'first_row': 5, 'month_col': 3, 'total_col': 4}
    assert task_rows(actual, mapping) == ROWS


@given(st.integers(1, 200), st.integers(1, 30), st.lists(st.integers(0, 10000), min_size=3, max_size=3))
def test_task_offsets_do_not_change_skill_identity(row, col, values):
    rows = [(m, v) for (m, _), v in zip(ROWS, values)]
    mapping = {'sheet': 'Data', 'first_row': row, 'month_col': col, 'total_col': col + 1}
    assert task_rows(snapshot(rows, row=row, col=col), mapping) == rows
    candidate = build_candidate(PROC)
    assert set(candidate.procedure) == {'action', 'method'}
    for key in mapping:
        assert key not in candidate.procedure


def test_task_mapping_required_and_chart_real_png(tmp_path, monkeypatch):
    path = tmp_path / 'file.xlsx'; path.write_bytes(b'not-a-zip')
    monkeypatch.setattr(h, '_read_via_excel_attach', lambda *a: snapshot(ROWS, row=5, col=3))
    store = SkillStore(str(tmp_path / 'store.json')); usage = UsageTracker(str(tmp_path / 'usage.json'))
    result = execute_p1(str(path), store, usage, 'task', app_open=True, procedure=PROC)
    assert result['status'] == 'NEEDS_TASK_MAPPING' and store.list() == []
    mapping = {**MAPPING, 'first_row': 5, 'month_col': 3, 'total_col': 4}
    result = execute_p1(str(path), store, usage, 'task', app_open=True, procedure=PROC, task_mapping=mapping)
    from pathlib import Path
    assert Path(result['chart_ref']).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    assert result['work']['forecast']['value'] == 1650
    assert store.list()[0].procedure == PROC
    assert not usage.list_shared_events()
