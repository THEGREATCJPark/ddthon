"""P0 request-scoped trust; no confirmation token fabricated by the Agent."""
import copy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys

import pytest

from skillloop.cli import _p0_team_scope_authorized, apply_requirements
from skillloop.descriptor import make_descriptor
from skillloop.gitsync import GitSyncAdapter
from skillloop.publish_pipeline import PublishPipeline, exact_ref
from skillloop.store import SkillStore
from skillloop.usage import UsageTracker
from tests.test_p0_two_packages import wheel


def setup_scope(tmp_path):
    source = tmp_path / 'packages'; source.mkdir()
    req, py = tmp_path / 'requirements.txt', tmp_path / 'python.exe'
    d = make_descriptor({'id': 'team-source', 'version': '3', 'origin': {'author': 'test'},
                         'applicability': {'signals': ['pip-install-fail']},
                         'procedure': {'action': 'pip-install', 'source': 'packages'}})
    store = SkillStore(str(tmp_path / 'store.json')); store.put(d)
    context = {'remote': 'test-remote', 'branch': 'trusted-team'}
    (tmp_path / 'sync-config.local.json').write_text(json.dumps(context), encoding='utf-8')
    # Fixture provenance is not evidence of an actual human review or real Git pull.
    PublishPipeline(store).record_remote_publication(d, {**context, 'commit': 'fixture'})
    policy = {'approved_skills': [], 'sources': {'packages': str(source)},
              'scoped_auto_apply': {'mode': 'same-request-p0', **context,
                  'skills': [exact_ref(d)], 'requirements': str(req), 'work_python': str(py),
                  'sources': {'packages': str(source)}}}
    return d, store, policy, req, py


@pytest.mark.parametrize('change', [
    'missing-policy', 'digest', 'remote', 'branch', 'python', 'requirements',
    'source', 'missing-evidence', 'rejected', 'demo', 'action', 'extra-command', 'corrupt-content',
])
def test_invalid_scope_never_authorizes(tmp_path, change):
    d, store, policy, req, py = setup_scope(tmp_path)
    assert _p0_team_scope_authorized(policy, d, store, req, py)
    scope = policy['scoped_auto_apply']
    if change == 'missing-policy': policy.pop('scoped_auto_apply')
    elif change == 'digest': scope['skills'][0]['digest'] = 'different'
    elif change in ('remote', 'branch'): scope[change] = 'different'
    elif change == 'python': py = tmp_path / 'other-python'
    elif change == 'requirements': req = tmp_path / 'other-requirements'
    elif change == 'source': scope['sources']['packages'] = str(tmp_path / 'other-source')
    elif change == 'missing-evidence': store.save_lifecycle_state(exact_ref(d), 'PUBLISHED', {})
    elif change == 'rejected': PublishPipeline(store).review(d, 'reject', 'test-reviewer')
    elif change == 'demo': d = replace(d, demo_seed=True)
    elif change == 'action': d.procedure['action'] = 'file-access'
    elif change == 'extra-command': d.procedure['command'] = 'unrequested'
    elif change == 'corrupt-content': d.origin['author'] = 'changed'
    assert not _p0_team_scope_authorized(policy, d, store, req, py)


def test_git_received_generic_skill_actual_cold_install_without_confirmation(tmp_path, capsys):
    d, sender_store, policy, req, unused_py = setup_scope(tmp_path)
    remote = tmp_path / 'remote.git'
    subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
    sender = GitSyncAdapter(tmp_path / 'sender', str(remote), 'trusted-team')
    # Transport test only; never claim this test fixture as a human-reviewed publication.
    assert sender.push_descriptors(sender_store.export_bundle([exact_ref(d)]))['ok']
    receiver_dir = tmp_path / '공백 작업'; receiver_dir.mkdir()
    store = SkillStore(str(receiver_dir / 'store.json'))
    usage = UsageTracker(str(receiver_dir / 'usage.json'))
    receiver = GitSyncAdapter(receiver_dir / 'mirror', str(remote), 'trusted-team')
    (receiver_dir / 'sync-config.local.json').write_text(json.dumps(receiver.context), encoding='utf-8')
    assert receiver.pull(store, usage)['ok']
    source = Path(policy['sources']['packages'])
    wheel(source, 'different-example', '4.2.0')
    subprocess.run([sys.executable, '-m', 'venv', str(receiver_dir / '.venv')], check=True, capture_output=True)
    py = receiver_dir / '.venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    empty = receiver_dir / 'empty'; empty.mkdir()
    config = py.parent.parent / 'pip.ini' if sys.platform == 'win32' else py.parent.parent / 'pip.conf'
    config.write_text(f'[global]\nno-index=true\nfind-links={empty.resolve().as_uri()}\ndisable-pip-version-check=true\n', encoding='utf-8')
    req = receiver_dir / 'requirements.txt'; req.write_text('different-example==4.2.0\n', encoding='utf-8')
    policy['imports'] = {'different-example': 'different_example'}
    policy['scoped_auto_apply'].update(receiver.context, requirements=str(req), work_python=str(py))
    policy_path = receiver_dir / 'policy.json'
    policy_path.write_text(json.dumps(policy), encoding='utf-8')
    # Real failure with scope removed must stop before installation/counting.
    denied = copy.deepcopy(policy); denied.pop('scoped_auto_apply')
    denied_path = receiver_dir / 'denied.json'; denied_path.write_text(json.dumps(denied), encoding='utf-8')
    assert apply_requirements(str(req), str(py), store.path, usage.path, 'same-run', str(denied_path)) == 2
    assert 'CONFIRMATION_REQUIRED' in capsys.readouterr().out
    assert UsageTracker(usage.path).current_count(d.id, d.version) == 0
    # User's same installation request can now use operator scope, without --confirm-skill.
    assert apply_requirements(str(req), str(py), store.path, usage.path, 'same-run', str(policy_path)) == 0
    output = capsys.readouterr().out
    assert 'install exit=1' in output and 'SCOPED_TEAM_POLICY' in output and 'counted=True' in output
    assert 'CONFIRMATION_REQUIRED' not in output
    probe = subprocess.run([str(py), '-c', "import different_example,importlib.metadata as m;assert m.version('different-example')=='4.2.0'"], capture_output=True)
    assert probe.returncode == 0
    assert UsageTracker(usage.path).current_count(d.id, d.version) == 1
    assert apply_requirements(str(req), str(py), store.path, usage.path, 'same-run', str(policy_path)) == 0
    assert 'INSTALL_OK_NO_REUSE' in capsys.readouterr().out
    assert UsageTracker(usage.path).current_count(d.id, d.version) == 1
