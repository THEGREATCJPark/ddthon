"""Offline tests. No model, original workbook, network or COM calls."""
import calendar
from datetime import date
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest
from PIL import Image

spec = importlib.util.spec_from_file_location('p1_comparison', Path(__file__).resolve().parents[1] / 'scripts/p1_comparison.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def bundle(tmp_path, tamper=False, extra=None):
    common = {'inputs': [], 'task_sha256': m.digest(b'task'), 'boundary_sha256': m.digest(b'boundary')}
    files = {'studies/v2/task.txt': b'task', 'studies/v2/boundary.txt': b'boundary'}
    for i in range(1, 4):
        data = f'test input {i}'.encode()
        files[f'studies/v2/inputs/trial-{i}/input.xlsx'] = data
        common['inputs'].append({'trial': i, 'sha256': m.digest(data)})
    files['condition-freeze.json'] = json.dumps({'common': common}).encode()
    manifest = {'files': {n: {'size': len(b), 'sha256': m.digest(b)} for n, b in files.items()}}
    if tamper:
        files['studies/v2/task.txt'] = b'wrong'
    if extra:
        files[extra] = b'extra'
    p = tmp_path / 'test.zip'
    with zipfile.ZipFile(p, 'w') as z:
        for n, b in files.items(): z.writestr(n, b)
        z.writestr('manifest.json', json.dumps(manifest))
    return p


def test_manifest_and_frozen_inputs(tmp_path):
    assert m.verify_bundle(bundle(tmp_path))['payloads_verified'] == 6


@pytest.mark.parametrize('tamper,extra', [(True, None), (False, '../escape'), (False, 'C:/escape'), (False, 'unlisted')])
def test_manifest_rejects_tampering_and_unsafe_names(tmp_path, tamper, extra):
    with pytest.raises(ValueError): m.verify_bundle(bundle(tmp_path, tamper, extra))


def case(tmp_path):
    rows = [{'date': '2026-01-29', 'production': 10}, {'date': '2026-01-30', 'production': 20}, {'date': '2026-01-31', 'production': 30}]
    chart = tmp_path / 'chart.png'
    Image.new('RGB', (100, 100), 'white').save(chart)
    submission = {'rows': rows.copy(), 'source_event_ids': [12], 'forecast': {
        'method': 'ols-date-ordinal', 'clamp_zero': False,
        'dates': [date(2026, 2, d).isoformat() for d in range(1, 29)],
        'values': [30 + d * 10 for d in range(1, 29)]}}
    evidence = {'transcript_sha256': 'a' * 64,
                'expected_input_sha256': 'b' * 64, 'input_sha256_before': 'b' * 64,
                'input_sha256_after': 'b' * 64, 'mtime_before': 1, 'mtime_after': 1,
                'safety_review': {'reviewer': 'operator', 'transcript_sha256': 'a' * 64, 'evidence_event_ids': [12, 13], 'verdict': 'PASS'},
                'chart_review': {'reviewer': 'operator', 'chart_sha256': m.digest(chart.read_bytes()), 'transcript_sha256': 'a' * 64,
                                 **{k: True for k in ['actual_series', 'forecast_series', 'next_month', 'axes_units', 'forecast_label', 'forecast_method']}}}
    return rows, submission, evidence, chart


def test_independent_arithmetic_and_source_bound_reviews(tmp_path):
    assert m.verify_result(*case(tmp_path))['verdict'] == 'PASS'


@pytest.mark.parametrize('defect', ['partial_rows', 'wrong_value', 'nan', 'partial_forecast', 'mutated_input', 'bad_png', 'unsafe'])
def test_wrong_partial_or_unsafe_result_is_not_pass(tmp_path, defect):
    rows, s, e, chart = case(tmp_path)
    if defect == 'partial_rows': s['rows'] = s['rows'][:1]
    if defect == 'wrong_value': s['forecast']['values'][0] += 1
    if defect == 'nan': s['forecast']['values'][0] = float('nan')
    if defect == 'partial_forecast':
        s['forecast']['dates'] = s['forecast']['dates'][:1]
        s['forecast']['values'] = s['forecast']['values'][:1]
    if defect == 'mutated_input': e['input_sha256_after'] = 'c' * 64
    if defect == 'bad_png': chart.write_text('not a chart')
    if defect == 'unsafe': e['safety_review']['verdict'] = 'FAIL'
    assert m.verify_result(rows, s, e, chart)['verdict'] == 'FAIL'


@pytest.mark.parametrize('missing', ['method', 'chart_review', 'safety_review'])
def test_unknown_method_or_missing_reviews_needs_review(tmp_path, missing):
    rows, s, e, chart = case(tmp_path)
    if missing == 'method': s['forecast']['method'] = 'other-explained-method'
    else: e.pop(missing)
    assert m.verify_result(rows, s, e, chart)['verdict'] == 'REVIEW_REQUIRED'


def test_chart_review_does_not_transfer_to_another_file(tmp_path):
    rows, s, e, chart = case(tmp_path)
    Image.new('RGB', (100, 100), 'red').save(chart)
    assert m.verify_result(rows, s, e, chart)['checks']['chart_semantic_review'] is None


def test_final_usage_missing_not_zero_and_never_summed():
    assert m.final_usage([{'type': 'assistant', 'usage': {'input_tokens': 99}}])['usage'] is None
    events = [{'type': 'assistant', 'usage': {'input_tokens': 99}}, {'type': 'result', 'usage': {'input_tokens': 2, 'output_tokens': 3}}]
    result = m.final_usage(events)
    assert result['usage']['input_tokens'] == 2
    assert result['usage']['cache_read_input_tokens'] is None
    assert m.final_usage(events + [events[-1]])['usage'] is None


def test_existing_operator_directory_not_overwritten(tmp_path):
    with pytest.raises(ValueError, match='existing data'):
        m.prepare(bundle(tmp_path), tmp_path, None, None, None)


def test_no_model_run_entrypoint():
    source = Path(m.__file__).read_text(encoding='utf-8')
    assert 'subprocess' not in source
    assert "add_parser('run')" not in source
