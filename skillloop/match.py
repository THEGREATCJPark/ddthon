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

from dataclasses import dataclass, field


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


def search(obs: FailureObservation, store) -> SearchOutcome:
    """관찰된 실패 신호와 applicability의 결정적 매칭으로 단일 MATCH 또는 상태 반환."""
    raise NotImplementedError("S7")
