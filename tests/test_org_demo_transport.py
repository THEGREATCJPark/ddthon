"""Selected-branch transport using real local Git, never a live demo database."""
import json
import subprocess
import pytest
from skillloop.gitsync import GitSyncAdapter
from skillloop.store import SkillStore
from skillloop.usage import UsageTracker
from skillloop.publish_pipeline import PublishPipeline, exact_ref, remote_matches
from skillloop.descriptor import make_descriptor


@pytest.mark.parametrize('branch', ['main', 'master', 'HEAD', '--upload-pack=x', '../x', 'bad ref', 'x..y'])
def test_invalid_data_branch_rejected(tmp_path, branch):
    with pytest.raises(ValueError):
        GitSyncAdapter(tmp_path / 'mirror', str(tmp_path / 'remote'), branch)
    assert not (tmp_path / 'mirror').exists()


def test_branch_and_remote_are_bound_and_other_branch_is_absent(tmp_path):
    remote = tmp_path / 'remote.git'
    subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
    a = GitSyncAdapter(tmp_path / 'a', str(remote), 'test-team')
    b = GitSyncAdapter(tmp_path / 'b', str(remote), 'test-team')
    store = SkillStore(str(tmp_path / 'source/store.json'))
    d = make_descriptor({'id': 'test-pip', 'version': '1', 'origin': {'author': 'test'},
                         'applicability': {'signals': ['pip-install-fail']},
                         'procedure': {'action': 'pip-install', 'source': 'test-source'}})
    store.put(d)
    # Tests transport ingestion only; not evidence of real human-approved publication.
    assert a.push_descriptors(store.export_bundle([exact_ref(d)]))['ok']
    other = SkillStore(str(tmp_path / 'receiver/store.json'))
    Path = __import__('pathlib').Path
    Path(other.path).parent.mkdir(parents=True)
    Path(other.path).with_name('sync-config.local.json').write_text(json.dumps(b.context), encoding='utf-8')
    usage = UsageTracker(str(tmp_path / 'receiver/usage.json'))
    assert b.pull(other, usage)['imported'] == 1
    assert b.pull(other, usage)['imported'] == 0
    assert PublishPipeline(other).reuse_eligible(d)
    from skillloop.org_aggregator import build_snapshot
    snap = build_snapshot(other, usage, PublishPipeline(other), b, my_alias='test')
    assert snap['organization']['viewer_contributions'] == 1
    refs = subprocess.run(['git', 'ls-remote', '--heads', str(remote)], capture_output=True, text=True).stdout
    assert 'test-team' in refs and 'team-skill-store' not in refs
    with pytest.raises(ValueError): GitSyncAdapter(tmp_path / 'a', str(remote), 'different-team').initialize()
    ev = b.last_sync()
    assert remote_matches(ev, b.context)
    assert not remote_matches({**ev, 'remote': 'other'}, b.context)
    assert not remote_matches({**ev, 'branch': 'other'}, b.context)
    assert not remote_matches(ev)  # selected branch is not the legacy default
