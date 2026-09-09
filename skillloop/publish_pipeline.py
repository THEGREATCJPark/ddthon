"""S3: exact-candidate review, fresh Replay, publication and read-only lifecycle view.

CJ continuation of the approved U2 contracts. C2 persists; only S3 decides state.
"""
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from .descriptor import compute_digest
from . import replay as verifier


def now():
    return datetime.now(timezone.utc).isoformat()


def exact_ref(candidate):
    return {key: getattr(candidate, key) for key in ('id', 'version', 'digest')}


def remote_matches(evidence, context=None):
    context = context or {'branch': 'team-skill-store'}
    return bool(evidence.get('commit') and evidence.get('branch') == context.get('branch', 'team-skill-store')
                and (not context.get('remote') or evidence.get('remote') == context['remote']))


class PublishPipeline:
    def __init__(self, store, transport_context=None):
        self.store = store
        config = Path(store.path).parent / 'sync-config.local.json'
        self.transport_context = (transport_context or
            (json.loads(config.read_text(encoding='utf-8')) if config.is_file() else {'branch': 'team-skill-store'}))

    def _check(self, candidate):
        if compute_digest(vars(candidate)) != candidate.digest:
            raise ValueError('INTEGRITY_ERROR: candidate content changed')
        # Re-read disk after a human response; a cached snapshot must not approve
        # content replaced while the candidate was on screen.
        current = type(self.store)(self.store.path).get(candidate.id, candidate.version)
        if current is None or exact_ref(current) != exact_ref(candidate):
            raise ValueError('CONFLICT: current stored candidate differs')

    def _evidence(self, candidate):
        self._check(candidate)
        record = self.store.load_lifecycle_state(exact_ref(candidate)) or {}
        return deepcopy(record.get('evidence', {}))

    def _save(self, candidate, state, evidence):
        self.store.save_lifecycle_state(exact_ref(candidate), state, evidence)
        return self.query_lifecycle_state(exact_ref(candidate))

    def propose(self, candidate):
        if compute_digest(vars(candidate)) != candidate.digest:
            raise ValueError('INTEGRITY_ERROR')
        result = self.store.put(candidate)
        if result.result == 'CONFLICT':
            raise ValueError('CONFLICT: candidate not overwritten')
        prior = self.store.load_lifecycle_state(exact_ref(candidate))
        if prior:
            return self.query_lifecycle_state(exact_ref(candidate))
        return self._save(candidate, 'PROPOSED', {})

    def review(self, candidate, decision, reviewer, approval_evidence=None):
        if decision not in ('approve', 'reject') or not reviewer.strip():
            raise ValueError('Explicit reviewer and approve/reject required')
        evidence = self._evidence(candidate)
        evidence['local_review_evidence'] = {
            'ref': exact_ref(candidate), 'decision': decision,
            'reviewer': reviewer, 'reviewed_at': now(),
        }
        if approval_evidence is not None:
            receipt = approval_evidence
            if (receipt.get('source') != 'claude-code-user'
                    or receipt.get('candidate_ref') != exact_ref(candidate)
                    or receipt.get('decision') != decision or receipt.get('reviewer') != reviewer
                    or not isinstance(receipt.get('user_response'), str)
                    or not receipt['user_response'].strip()):
                raise ValueError('Exact candidate and explicit user response required')
            evidence['local_review_evidence']['approval_source'] = receipt['source']
            evidence['local_review_evidence']['user_response'] = receipt['user_response']
        evidence.pop('replay', None)  # A new review never inherits an earlier Replay.
        return self._save(candidate, 'APPROVED' if decision == 'approve' else 'REJECTED', evidence)

    def replay(self, candidate, env):
        evidence = self._evidence(candidate)
        approval = evidence.get('local_review_evidence', {})
        if approval.get('decision') != 'approve' or approval.get('ref') != exact_ref(candidate):
            raise ValueError('REVIEW_REQUIRED: exact candidate human approval missing')
        result = verifier.replay(candidate, env)  # no caller-supplied PASS or first artifact
        evidence['replay'] = asdict(result)
        return self._save(candidate, 'LOCALLY_APPROVED' if self._gate(candidate, evidence) else 'BLOCKED', evidence)

    def _gate(self, candidate, evidence):
        approval = evidence.get('local_review_evidence', {})
        replay = evidence.get('replay', {})
        ev = replay.get('evidence', {})
        access = ev.get('access_evidence', {})
        identity_ok = (approval.get('decision') == 'approve' and bool(approval.get('reviewer'))
                and approval.get('ref') == replay.get('candidate_ref') == exact_ref(candidate)
                and replay.get('verdict') == 'PASS'
                and ev.get('candidate_digest_verified') is True
                and ev.get('replay_independent') is True
                and ev.get('reused_first_run_result') is False)
        if candidate.procedure.get('action') == 'pip-install':
            pip = ev.get('pip_verification', {})
            return bool(identity_ok and ev.get('action') == 'pip-install'
                        and pip.get('pip_exit_code') == 0
                        and all(pip.get(k) is True for k in
                                ('installed_check', 'version_check', 'import_check', 'is_real_success'))
                        and ev.get('clean_before') is True)
        return (identity_ok and candidate.procedure.get('action') == 'file-access'
                and access.get('original_unchanged') is True
                and access.get('save_called') is False
                and access.get('workbook_readable') is True
                and bool(access.get('sha256_before'))
                and access.get('sha256_before') == access.get('sha256_after'))

    def publish(self, candidate, transport):
        evidence = self._evidence(candidate)
        if not self._gate(candidate, evidence):
            return self._save(candidate, 'BLOCKED', evidence)
        self._save(candidate, 'LOCALLY_APPROVED', evidence)
        blob = self.store.export_bundle([exact_ref(candidate)])
        result = transport.push_descriptors(blob)
        evidence['last_publish_attempt'] = result
        context = getattr(transport, 'context', self.transport_context)
        if result.get('ok') is True and remote_matches(result, context):
            evidence['remote_publish_evidence'] = result
            state = 'PUBLISHED'
        else:
            state = 'PUBLISH_PENDING'
        return self._save(candidate, state, evidence)

    def record_remote_publication(self, candidate, transport_evidence):
        """Called after actual fetch+content import, not from a remote state string."""
        evidence = self._evidence(candidate)
        if not remote_matches(transport_evidence, self.transport_context):
            raise ValueError('Missing actual transport evidence')
        evidence['remote_publish_evidence'] = deepcopy(transport_evidence)
        # Remote origin is evidence of sharing, never this environment's review/Replay.
        prior = self.store.load_lifecycle_state(exact_ref(candidate))
        state = prior['state'] if prior and evidence.get('local_review_evidence') else 'PUBLISHED'
        return self._save(candidate, state, evidence)

    def reuse_eligible(self, candidate):
        evidence = self._evidence(candidate)
        record = self.store.load_lifecycle_state(exact_ref(candidate)) or {}
        if record.get('state') in ('PROPOSED', 'REJECTED', 'BLOCKED', 'APPROVED'):
            return False
        remote = evidence.get('remote_publish_evidence', {})
        return bool(self._gate(candidate, evidence) or
                    (record.get('state') == 'PUBLISHED' and remote_matches(remote, self.transport_context)))

    def query_lifecycle_state(self, ref):
        record = self.store.load_lifecycle_state(ref)
        if not record:
            return None
        evidence = record.get('evidence', {})
        return {'ref': dict(ref), 'state': record['state'], 'lifecycle_state': record['state'],
                'local_review_evidence': deepcopy(evidence.get('local_review_evidence')),
                'remote_publish_evidence': deepcopy(evidence.get('remote_publish_evidence')),
                'replay': deepcopy(evidence.get('replay'))}

    def list_lifecycle_states(self, filter=None):
        rows = [self.query_lifecycle_state({k: rec[k] for k in ('id', 'version', 'digest')})
                for rec in self.store.list_lifecycle_records()]
        return [row for row in rows if not filter or row['state'] == filter]
