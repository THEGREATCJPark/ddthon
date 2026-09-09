"""Real pip Replay; explicit test-review fixture, not real user approval."""
from copy import deepcopy
from dataclasses import asdict
from types import SimpleNamespace
import pytest
from skillloop import envharness_p0 as harness
from skillloop.descriptor import make_descriptor
from skillloop.replay import PipReplayContext, replay
from skillloop.publish_pipeline import PublishPipeline, exact_ref
from skillloop.store import SkillStore


def candidate():
    return make_descriptor({'id': 'pip-source-test', 'version': '1.0', 'origin': {'author': 'test'},
                            'applicability': {'signals': ['pip-install-fail']},
                            'procedure': {'action': 'pip-install', 'source': 'custom-alias'}})


def test_real_pip_replay_and_strict_gate(tmp_path):
    harness.prepare()
    d = candidate()
    store = SkillStore(str(tmp_path / 'store.json'))
    pipeline = PublishPipeline(store)
    pipeline.propose(d)
    transport = SimpleNamespace(context={'branch': 'isolated-test', 'remote': 'test-remote'},
        push_descriptors=lambda blob: {'ok': True, 'commit': 'test-only', 'branch': 'isolated-test', 'remote': 'test-remote'})
    assert pipeline.publish(d, transport)['state'] == 'BLOCKED'
    pipeline.review(d, 'approve', 'test-fixture-reviewer')
    assert pipeline.publish(d, transport)['state'] == 'BLOCKED'
    context = PipReplayContext(harness.TARGET_PKG, harness.TARGET_VERSION, harness.TARGET_IMPORT,
                              {'custom-alias': harness.resolve_index('allow')})
    report = pipeline.replay(d, context)
    assert report['state'] == 'LOCALLY_APPROVED'
    assert report['replay']['evidence']['clean_before'] is True
    assert not (tmp_path / 'usage.json').exists()
    assert pipeline.publish(d, transport)['state'] == 'PUBLISHED'
    original = pipeline._evidence(d)
    for flag in ('installed_check', 'version_check', 'import_check', 'is_real_success'):
        broken = deepcopy(original)
        broken['replay']['evidence']['pip_verification'][flag] = False
        assert not pipeline._gate(d, broken)
    broken = deepcopy(original); broken['replay']['evidence']['action'] = 'file-access'
    assert not pipeline._gate(d, broken)
    changed = deepcopy(d); changed.procedure['source'] = 'different'
    with pytest.raises(ValueError): pipeline.publish(changed, transport)
    assert replay(d, PipReplayContext('anything', '1', 'anything', {})).verdict == 'NOT_RUN'


def test_conversation_receipt_requires_exact_ref_and_actual_response(tmp_path):
    from skillloop import cli
    import json
    store = SkillStore(str(tmp_path / 'store.json')); d = candidate()
    PublishPipeline(store).propose(d)
    receipt = {'source': 'claude-code-user', 'candidate_ref': exact_ref(d),
               'decision': 'approve', 'reviewer': 'test-only', 'user_response': ''}
    file = tmp_path / 'approval.json'
    args = ['review', '--store', store.path, '--id', d.id, '--version', d.version,
            '--decision', 'approve', '--reviewer', 'test-only', '--approval-file', str(file)]
    file.write_text(json.dumps(receipt), encoding='utf-8')
    assert cli.main(args) == 2
    assert PublishPipeline(store).query_lifecycle_state(exact_ref(d))['state'] == 'PROPOSED'
    receipt['user_response'] = 'Approve this displayed candidate (test receipt only)'
    receipt['candidate_ref']['digest'] = 'wrong'
    file.write_text(json.dumps(receipt), encoding='utf-8')
    assert cli.main(args) == 2
    receipt['candidate_ref'] = exact_ref(d)
    file.write_text(json.dumps(receipt), encoding='utf-8')
    assert cli.main(args) == 0
    recorded = PublishPipeline(SkillStore(store.path)).query_lifecycle_state(exact_ref(d))
    assert recorded['local_review_evidence']['user_response'] == receipt['user_response']
    assert recorded['state'] == 'APPROVED' and recorded['replay'] is None


def test_candidate_changed_on_disk_while_awaiting_review_is_rejected(tmp_path):
    import json
    from pathlib import Path
    store = SkillStore(str(tmp_path / 'store.json')); d = candidate()
    pipeline = PublishPipeline(store); pipeline.propose(d)
    content = json.loads(Path(store.path).read_text(encoding='utf-8'))
    content['skills'] = {}
    Path(store.path).write_text(json.dumps(content), encoding='utf-8')
    with pytest.raises(ValueError, match='CONFLICT'):
        pipeline.review(d, 'approve', 'test-only')
