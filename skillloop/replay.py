"""C6 — ReplayVerifier: exact candidate의 독립 Replay.

소유(단일 수정자): B (한석훈)
확정 계약(FD §4, 계약 5 — U2가 여기서 정의하고 S3가 소비):

    replay(candidate: Descriptor, env: EnvContext) -> ReplayResult
    # ReplayResult = {verdict: PASS|FAIL|NOT_RUN, candidate_ref:{id,version,digest}, evidence}

독립성·정직성(FR-P1-7 / NFR-TEST-2):
    - **별도 실행 문맥**에서 candidate의 환경 접근 procedure를 `run_file_access_procedure`로
      **새로 재수행**한다. 최초 실행(S1)의 artifact·획득 content·성공 판정을 **재사용하지 않는다**.
      → 시그니처가 candidate/env만 받고 최초 결과 인자를 두지 않아 구조적으로 재사용이 불가능하다.
    - verdict는 화면 문구가 아닌 **실제 접근 효과**(새로 획득한 셀 content) + read-only 근거
      (mtime·sha256 실측 무변경, save_called=False) 기반으로 산출한다.
    - **환경 미준비(Excel 미설치/미열림) → NOT_RUN**(게시 금지). 실행 후 미충족은 **FAIL**.
    - candidate_ref.digest는 게이트 동일성 확인용으로 함께 반환(승인·게시 판정은 S3가 별도 수행).
      Replay PASS ≠ 사람 승인 ≠ 원격 게시 완료(셋은 분리 유지).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json

from skillloop import descriptor as _desc
from skillloop.envharness_p1 import EnvContext, run_file_access_procedure

# verdict 상수(게이트 소비자 S3와 공유하는 계약 5 어휘).
PASS = "PASS"
FAIL = "FAIL"
NOT_RUN = "NOT_RUN"


@dataclass
class ReplayResult:
    """독립 Replay 결과. verdict는 새로 획득한 실제 효과 기반."""
    verdict: str                       # PASS | FAIL | NOT_RUN
    candidate_ref: dict                # {id, version, digest} — exact candidate 동일성
    evidence: dict = field(default_factory=dict)


def _candidate_ref(candidate) -> dict:
    """candidate의 정확한 식별자(id/version/digest)만 추출. 게이트 동일성 확인용."""
    return {
        "id": candidate.id,
        "version": candidate.version,
        "digest": candidate.digest,
    }


def replay(candidate, env: EnvContext) -> ReplayResult:
    """exact candidate의 접근 procedure를 별도 문맥에서 새로 재수행해 verdict 산출.

    - candidate.procedure를 `run_file_access_procedure(procedure, env)`로 **새로** 실행한다.
      (최초 실행 content/evidence를 인자로 받지 않으므로 재사용 불가 — 항상 새 접근.)
    - env 미준비(app_open=False)·attach 미가용(method="none") → NOT_RUN(게시 불가).
    - 실행됐으나 접근 효과·read-only 기준 미충족 → FAIL.
    - 접근 성공(AccessResult.ok=True) → PASS.
    """
    ref = _candidate_ref(candidate)

    # candidate 동일성 근거: 내용에서 digest를 재계산해 저장된 digest와 대조(게이트 소비용).
    # 불일치는 접근 전에 FAIL. S3도 exact ref와 무결성 근거를 검사한다.
    try:
        content = {k: getattr(candidate, k) for k in _desc.CONTENT_KEYS}
        recomputed = _desc.compute_digest(content)
        digest_verified = (recomputed == candidate.digest)
    except Exception:
        recomputed = None
        digest_verified = False

    evidence: dict = {
        "replay_independent": True,          # 별도 실행 문맥·새 접근(최초 결과 미재사용)
        "reused_first_run_result": False,    # 시그니처상 최초 결과 인자 없음 → 구조적 미재사용
        "candidate_digest_verified": digest_verified,
        "recomputed_digest": recomputed,
        "app_open": env.app_open,
    }

    if not digest_verified:
        evidence["reason"] = "candidate digest mismatch; access not invoked"
        evidence["ran"] = False
        return ReplayResult(verdict=FAIL, candidate_ref=ref, evidence=evidence)

    # 환경 미준비 → 실행하지 않고 NOT_RUN(게시 금지). 강제 통과·연출 없음.
    if not env.app_open:
        evidence["reason"] = "environment not ready (app_open=False) — Excel not open/installed"
        return ReplayResult(verdict=NOT_RUN, candidate_ref=ref, evidence=evidence)

    # 별도 문맥에서 candidate의 procedure를 **새로** 재수행(최초 실행 산출물 미참조).
    access = run_file_access_procedure(candidate.procedure, env)
    evidence["access_method"] = access.method
    evidence["access_ok"] = access.ok
    evidence["access_evidence"] = access.evidence
    # 새로 획득한 content의 형태 요약만 근거로 남긴다(최초 실행 content가 아님).
    evidence["replay_obtained_sheets"] = (
        len(access.content.get('sheets', [])) if isinstance(access.content, dict) else 0
    )

    # attach 미가용/미열림 → 실행 불가 → NOT_RUN(FAIL 아님).
    if access.method == "none" and access.evidence.get("ran") is not True:
        evidence["reason"] = "excel attach unavailable — access procedure could not run"
        return ReplayResult(verdict=NOT_RUN, candidate_ref=ref, evidence=evidence)

    # 실행됨: 실제 접근 효과 + read-only 근거로 PASS/FAIL 판정.
    ae = access.evidence
    valid = (access.ok is True and ae.get("original_unchanged") is True
             and ae.get("workbook_readable") is True and ae.get("save_called") is False
             and bool(ae.get("sha256_before"))
             and ae.get("sha256_before") == ae.get("sha256_after")
             and ae.get("mtime_before") is not None
             and ae.get("mtime_before") == ae.get("mtime_after"))
    evidence["fresh_content_digest"] = hashlib.sha256(
        json.dumps(access.content, ensure_ascii=False).encode("utf-8")).hexdigest()
    verdict = PASS if valid else FAIL
    return ReplayResult(verdict=verdict, candidate_ref=ref, evidence=evidence)
