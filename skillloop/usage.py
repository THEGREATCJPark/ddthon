"""C3 — UsageTracker: 실제 재사용 기록의 유일한 쓰기 주체(카운트 단독 소유).

소유(단일 수정자): CJ
계약(Code Plan §1, §3):
    - new_execution_id() -> str       새 논리적 실행 시작 시 cli가 1회 호출(발급 지점)
    - build_evidence(skill_ref, verification, run_id, demo_seed) -> ReuseEvidence
    - record_actual_reuse(evidence) -> RecordResult
    - current_count(id, version) -> int

규칙(R3, 정합화 1·2):
    - 카운트 증가는 오직 record_actual_reuse. store.put(C2)은 절대 카운트 변경 없음.
    - counted=True ⟺ is_real_success & !demo_seed & run_id 미기록(새 실행).
    - 동일 run_id 재기록(재검증/재시도/재시작) → counted=False, reason="same-execution".
    - run_id는 '실행'을 식별. 같은 문제의 다른 환경 재사용은 새 run_id → 각각 +1.
    - run_id 발급은 new_execution_id뿐. S1/검증은 발급하지 않고 전달만 받는다.
저장: 로컬 JSON. seen_run_ids(set) 영속화로 실행 단위 dedup.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReuseEvidence:
    skill_ref: dict              # {id, version} — 어떤 Skill을 재사용했는지
    is_real_success: bool        # clean+pip 종료코드+설치·버전+import 검증 통과 여부
    verification: dict           # 검증 방법·결과 상세
    run_id: str                  # 안정적 실행 식별자(호출자 발급, 전달만)
    demo_seed: bool = False       # 미리 만든 실적이면 True(실적 카운트 제외)
    timestamp: str = ""


@dataclass
class RecordResult:
    counted: bool
    new_count: int
    reason: str = ""             # "same-execution" | "not-real-success" | "demo-seed" | "ok"


def new_execution_id() -> str:
    """새 논리적 실행 식별자 발급. cli(run_p0)가 실행 시작 시 1회만 호출."""
    raise NotImplementedError("S4")


def build_evidence(skill_ref: dict, verification: dict, run_id: str,
                   demo_seed: bool = False) -> ReuseEvidence:
    """검증 결과로부터 ReuseEvidence 구성. run_id는 호출자가 전달."""
    raise NotImplementedError("S4")


def record_actual_reuse(evidence: ReuseEvidence) -> RecordResult:
    """실제 재사용 성공만 +1. run_id로 실행 단위 dedup. 카운트 쓰기의 유일 경로."""
    raise NotImplementedError("S4")


def current_count(id: str, version: str) -> int:
    """(id, version)의 현재 actual_reuse 카운트."""
    raise NotImplementedError("S4")
