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
저장: 로컬 JSON. seen_run_ids 영속화로 실행 단위 dedup.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

_KEYSEP = "\x1f"


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
    reason: str = ""             # "ok" | "same-execution" | "not-real-success" | "demo-seed"


def _key(id: str, version: str) -> str:
    return f"{id}{_KEYSEP}{version}"


def new_execution_id() -> str:
    """새 논리적 실행 식별자 발급. cli(run_p0)가 실행 시작 시 1회만 호출."""
    return uuid.uuid4().hex


def build_evidence(skill_ref: dict, verification: dict, run_id: str,
                   demo_seed: bool = False) -> ReuseEvidence:
    """검증 결과로부터 ReuseEvidence 구성. run_id는 호출자가 전달(재발급 없음)."""
    return ReuseEvidence(
        skill_ref=dict(skill_ref),
        is_real_success=bool(verification.get("is_real_success", False)),
        verification=dict(verification),
        run_id=run_id,
        demo_seed=demo_seed,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


class UsageTracker:
    """카운트·seen_run_ids를 로컬 JSON에 영속화. 카운트 쓰기의 유일 경로."""

    def __init__(self, path: str):
        self.path = path
        self._counts: dict[str, int] = {}
        self._seen: set[str] = set()
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._counts = data.get("counts", {})
            self._seen = set(data.get("seen_run_ids", []))

    def _save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                {"counts": self._counts, "seen_run_ids": sorted(self._seen)},
                f, ensure_ascii=False, sort_keys=True,
            )
        os.replace(tmp, self.path)

    def record_actual_reuse(self, evidence: ReuseEvidence) -> RecordResult:
        key = _key(evidence.skill_ref["id"], evidence.skill_ref["version"])
        current = self._counts.get(key, 0)
        if not evidence.is_real_success:
            return RecordResult(False, current, reason="not-real-success")
        if evidence.demo_seed:
            return RecordResult(False, current, reason="demo-seed")
        if evidence.run_id in self._seen:
            # 동일 실행의 재검증·재시도·재시작 → 중복 +1 방지
            return RecordResult(False, current, reason="same-execution")
        self._counts[key] = current + 1
        self._seen.add(evidence.run_id)
        self._save()
        return RecordResult(True, self._counts[key], reason="ok")

    def current_count(self, id: str, version: str) -> int:
        return self._counts.get(_key(id, version), 0)

    def seed_count(self, id: str, version: str, count: int) -> None:
        """DEMO_SEED(미리 만든 실적) 주입 — 실제 재사용 경로와 분리된 시연용."""
        self._counts[_key(id, version)] = count
        self._save()


# --- 프로세스 기본 트래커(모듈 레벨 편의 함수) ---
_DEFAULT_PATH = os.environ.get(
    "SKILLLOOP_USAGE", os.path.join(os.path.expanduser("~"), ".skillloop", "usage.json")
)
_default: UsageTracker | None = None


def _default_tracker() -> UsageTracker:
    global _default
    if _default is None:
        _default = UsageTracker(_DEFAULT_PATH)
    return _default


def record_actual_reuse(evidence: ReuseEvidence) -> RecordResult:
    return _default_tracker().record_actual_reuse(evidence)


def current_count(id: str, version: str) -> int:
    return _default_tracker().current_count(id, version)
