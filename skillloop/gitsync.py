"""C4: immutable JSON bundles in an explicitly separate team-store Git mirror."""
import hashlib
import json
from pathlib import Path
import subprocess

from .publish_pipeline import PublishPipeline, now

BRANCH = 'team-skill-store'


class GitSyncAdapter:
    def __init__(self, mirror_path, remote, branch=BRANCH):
        self.path = Path(mirror_path).resolve()
        self.remote = str(remote)
        if not self.remote or self.remote.startswith('-'):
            raise ValueError('Explicit remote required')
        self.branch = str(branch)
        valid = subprocess.run(['git', 'check-ref-format', '--branch', self.branch],
                               capture_output=True, timeout=10)
        if valid.returncode or self.branch.startswith('-') or self.branch in ('main', 'master', 'HEAD'):
            raise ValueError('Explicit non-source Git data branch required')
        self.context = {'remote': self.remote, 'branch': self.branch}

    def _git(self, *args, check=True):
        p = subprocess.run(['git', '-C', str(self.path), *args], capture_output=True,
                           text=True, encoding='utf-8', errors='replace', timeout=60)
        if check and p.returncode:
            # Git errors may contain credential-bearing remote URLs. Do not echo them.
            raise RuntimeError(f'Git {args[0]} failed (exit={p.returncode}); local data retained')
        return p

    def _validate(self):
        marker = self.path / '.git/skillloop-mirror.json'
        registered = json.loads(marker.read_text(encoding='utf-8')) if marker.is_file() else {}
        if registered.get('remote') != self.remote or registered.get('branch', BRANCH) != self.branch:
            raise ValueError('Not the registered isolated SkillLoop mirror')
        if self._git('remote', 'get-url', 'origin').stdout.strip() != self.remote:
            raise ValueError('Mirror origin changed')
        if self._git('branch', '--show-current').stdout.strip() != self.branch:
            raise ValueError('Mirror must be on the registered data branch')
        if self._git('status', '--porcelain').stdout.strip():
            raise ValueError('Mirror has uncommitted changes; retained for inspection')

    def initialize(self):
        if (self.path / '.git').exists():
            self._validate()
            return
        if self.path.exists() and any(self.path.iterdir()):
            raise ValueError('Use a new empty mirror directory')
        self.path.mkdir(parents=True, exist_ok=True)
        self._git('init', '-b', self.branch)
        self._git('config', 'user.name', 'SkillLoop transport')
        self._git('config', 'user.email', 'skillloop@example.invalid')
        self._git('remote', 'add', 'origin', self.remote)
        (self.path / '.git/skillloop-mirror.json').write_text(json.dumps(self.context), encoding='utf-8')
        refs = self._git('ls-remote', '--heads', 'origin', self.branch).stdout.strip()
        if refs:
            self._git('fetch', 'origin', self.branch)
            self._git('reset', '--hard', 'FETCH_HEAD')  # only the just-created, empty mirror

    def _fetch(self):
        self.initialize()
        self._validate()
        if self._git('ls-remote', '--heads', 'origin', self.branch).stdout.strip():
            self._git('fetch', 'origin', self.branch)
            self._git('merge', '--no-edit', 'FETCH_HEAD')

    def _push(self, kind, blob):
        try:
            json.loads(blob.decode('utf-8'))
            self._fetch()
            digest = hashlib.sha256(blob).hexdigest()
            target = self.path / kind / (digest + '.json')
            if not target.resolve().is_relative_to(self.path) or target.parent.is_symlink():
                raise ValueError('Bundle path escapes mirror')
            target.parent.mkdir(exist_ok=True)
            if target.exists() and target.read_bytes() != blob:
                raise ValueError('Bundle content mismatch')
            target.write_bytes(blob)
            self._git('add', '--', f'{kind}/{digest}.json')
            if self._git('diff', '--cached', '--quiet', check=False).returncode:
                self._git('commit', '-m', f'Share {kind} {digest[:12]}')
            self._git('push', 'origin', f'HEAD:refs/heads/{self.branch}')
            commit = self._git('rev-parse', 'HEAD').stdout.strip()
            remote_commit = self._git('ls-remote', '--heads', 'origin', self.branch).stdout.split()[0]
            if remote_commit != commit:
                raise RuntimeError('Remote confirmation differs; retry required')
            evidence = {'ok': True, 'commit': commit, **self.context,
                        'synced_at': now(), 'branch_revision': commit,
                        'queryable_range': 'shared Git bundles', 'bundle': f'{kind}/{digest}.json'}
            self._save_meta(evidence)
            return evidence
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
            return {'ok': False, 'branch': self.branch, 'error': type(exc).__name__, 'retryable': True}

    def push_descriptors(self, blob):
        return self._push('skills', blob)

    def push_shared_usage(self, blob):
        return self._push('reuse', blob)

    def _save_meta(self, evidence):
        (self.path / '.git/skillloop-last-sync.json').write_text(json.dumps(evidence), encoding='utf-8')

    def last_sync(self):
        p = self.path / '.git/skillloop-last-sync.json'
        return json.loads(p.read_text(encoding='utf-8')) if p.is_file() else None

    def pull(self, store, usage):
        try:
            self._fetch()
            commit = self._git('rev-parse', 'HEAD').stdout.strip()
            evidence = {'ok': True, 'commit': commit, **self.context, 'synced_at': now(),
                        'branch_revision': commit, 'queryable_range': 'shared Git bundles'}
            imported, conflicts, events = 0, 0, 0
            pipeline = PublishPipeline(store, transport_context=self.context)
            for kind in ('skills', 'reuse'):
                for p in sorted((self.path / kind).glob('*.json')):
                    if p.is_symlink() or not p.resolve().is_relative_to(self.path):
                        raise ValueError('Shared bundle cannot be a symlink')
                    blob = p.read_bytes()
                    if hashlib.sha256(blob).hexdigest() != p.stem:
                        raise ValueError('Shared bundle hash mismatch')
                    if kind == 'skills':
                        results = store.import_bundle(blob)
                        for item, result in zip(json.loads(blob)['skills'], results):
                            if result.result == 'CONFLICT':
                                conflicts += 1
                                continue
                            content = item['content']
                            candidate = store.get(content['id'], content['version'])
                            pipeline.record_remote_publication(candidate, {**evidence, 'bundle': f'{kind}/{p.name}'})
                            imported += result.result == 'STORED'
                    else:
                        def exists(ref):
                            d = store.get(ref.get('id'), ref.get('version'))
                            return d is not None and d.digest == ref.get('digest')
                        events += sum(r['applied'] for r in usage.import_shared_usage(blob, local_ref_exists=exists))
            self._save_meta(evidence)
            return {**evidence, 'imported': imported, 'conflicts': conflicts, 'events': events}
        except (OSError, ValueError, RuntimeError, KeyError, subprocess.TimeoutExpired) as exc:
            return {'ok': False, 'error': type(exc).__name__, 'retryable': True}


def init_team_store(mirror_path=None, remote=None, branch=BRANCH):
    if not mirror_path or not remote:
        raise ValueError('Explicit separate mirror path and remote required')
    GitSyncAdapter(mirror_path, remote, branch).initialize()
    return 0
