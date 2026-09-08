"""C5 — SkillSearchMatcher: 결정적 검색 + applicability 매칭 + 근거.

소유(단일 수정자): A (최호길) — 이 파일은 A만 편집. 인계 후 CJ 동시 수정 금지.
계약(Code Plan §1):
    - search(obs, store) -> SearchOutcome

규칙(R4, RU1, 정정 Q2):
    - 유효 후보 = applicability.signals 만족.
    - 다수여도 NO_MATCH 아님 → 안정 정렬(적합도↓, version↓, id↑)+동점규칙 → 단일 MATCH+근거.
    - NO_MATCH = 유효 후보 0건일 때만.
    - 내부오류/시간초과/미호출은 ERROR/TIMEOUT/NOT_INVOKED로 별도 구분.
CJ 소유 계약(store)은 호출만.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class FailureObservation:
    command: str
    target_pkg: str
    error_signature: str
    exit_code: int


@dataclass
class SearchOutcome:
    status: str                          # "MATCH"|"NO_MATCH"|"ERROR"|"TIMEOUT"|"NOT_INVOKED"
    descriptor: object = None            # MATCH일 때 선택된 Descriptor
    rationale: str = ""                  # 선택/미선택 근거
    candidates_considered: int = 0


# 상태 상수(문자열; enum 없음). NO_MATCH·성공과 오류/시간초과/미호출을 명확히 구분.
STATUS_MATCH = "MATCH"
STATUS_NO_MATCH = "NO_MATCH"
STATUS_ERROR = "ERROR"
STATUS_TIMEOUT = "TIMEOUT"
STATUS_NOT_INVOKED = "NOT_INVOKED"


def _match_score(signal: str, error_signature: str) -> int:
    """신호 적합도 점수. 2=정확 일치, 1=상위 네임스페이스(prefix) 일치, 0=불일치.

    관찰 신호가 "pip-install-fail:skillloop-demo-pkg"일 때
    - "pip-install-fail:skillloop-demo-pkg" → 2 (정확)
    - "pip-install-fail"                    → 1 (상위 네임스페이스)
    - "pip-install-fail:other-pkg"          → 0
    """
    if signal == error_signature:
        return 2
    if error_signature.startswith(signal + ":"):
        return 1
    return 0


def _signal_fit(descriptor, obs: FailureObservation) -> int:
    """descriptor.applicability.signals와 관찰 신호의 최고 적합도(0이면 유효 후보 아님)."""
    applicability = getattr(descriptor, "applicability", None) or {}
    signals = applicability.get("signals", [])
    if not isinstance(signals, (list, tuple)):
        raise TypeError(
            f"applicability.signals must be a list, got {type(signals).__name__}"
        )
    scores = [_match_score(s, obs.error_signature) for s in signals]
    return max(scores) if scores else 0


def _version_key(version: str):
    """version 문자열의 결정적 비교 키. 숫자 컴포넌트는 정수로, 그 외는 문자열로.

    (1, int) / (0, str) 형태로 통일해 int↔str 비교 예외 없이 전순서를 보장.
    """
    key = []
    for part in str(version).split("."):
        if part.isdigit():
            key.append((1, int(part)))
        else:
            key.append((0, part))
    return key


def _rank(scored):
    """(descriptor, fit) 목록을 (적합도↓, version↓, id↑)로 안정 정렬.

    안정 정렬 3-pass: id 오름차순 → version 내림차순 → 적합도 내림차순.
    마지막 pass가 1차 기준이 되고, 동점은 앞선 pass 순서를 보존한다.
    """
    ranked = sorted(scored, key=lambda t: t[0].id)                                   # id ↑
    ranked = sorted(ranked, key=lambda t: _version_key(t[0].version), reverse=True)  # version ↓
    ranked = sorted(ranked, key=lambda t: t[1], reverse=True)                        # fit ↓
    return ranked


def _rationale(selected, fit: int, ranked) -> str:
    listed = ", ".join(f"{d.id}@{d.version}(fit={f})" for d, f in ranked)
    return (
        f"MATCH {selected.id}@{selected.version} (fit={fit}) - "
        f"유효 후보 {len(ranked)}건 중 결정적 선택[적합도 내림차순, version 내림차순, id 오름차순]. "
        f"ranked=[{listed}]"
    )


def search(obs: FailureObservation, store, budget_s: float | None = None) -> SearchOutcome:
    """관찰된 실패 신호와 applicability의 결정적 매칭으로 단일 MATCH 또는 상태 반환.

    - 유효 후보(적합도>0)가 다수여도 NO_MATCH가 아니라 결정적 단일 선택.
    - NO_MATCH는 실제 검색을 수행하고 유효 후보가 0건일 때만.
    - 신호 없음 → NOT_INVOKED, 검색 중 예외 → ERROR, budget 초과 → TIMEOUT
      (어느 것도 NO_MATCH로 위장하지 않는다).
    budget_s는 선택적 검색 예산(초). 미지정(None)이면 시간초과를 검사하지 않는다.
    주의: budget_s는 store.list()·스코어링 완료 후 경과시간을 검사하는 사후(post-scan)
    방식이며, 진행 중인 검색을 선점 중단하지는 않는다(P0 인메모리 검색 범위).
    """
    signature = getattr(obs, "error_signature", "") or ""
    if not signature.strip():
        return SearchOutcome(
            status=STATUS_NOT_INVOKED,
            rationale="관찰된 실패 신호 없음 - 검색 미수행(NOT_INVOKED)",
        )

    start = time.monotonic()
    try:
        descriptors = store.list()
        scored = []
        for d in descriptors:
            fit = _signal_fit(d, obs)
            if fit > 0:
                scored.append((d, fit))
    except Exception as exc:  # 검색 내부 오류는 NO_MATCH로 위장 금지
        return SearchOutcome(status=STATUS_ERROR, rationale=f"검색 오류: {exc!r}")

    if budget_s is not None and (time.monotonic() - start) > budget_s:
        return SearchOutcome(
            status=STATUS_TIMEOUT,
            rationale=f"검색 예산 초과({budget_s}s) - TIMEOUT",
            candidates_considered=len(scored),
        )

    if not scored:
        return SearchOutcome(
            status=STATUS_NO_MATCH,
            rationale=f"유효 후보 없음(스캔 {len(descriptors)}건, 유효 0건)",
            candidates_considered=0,
        )

    ranked = _rank(scored)
    selected, fit = ranked[0]
    return SearchOutcome(
        status=STATUS_MATCH,
        descriptor=selected,
        rationale=_rationale(selected, fit, ranked),
        candidates_considered=len(scored),
    )
