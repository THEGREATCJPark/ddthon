"""C3 — UsageTracker: 실제 재사용 기록의 유일한 쓰기 주체(카운트 단독 소유).

소유(단일 수정자): CJ
계약(Code Plan §1, §3 + U2 공통 의존성 C-d):
    - new_execution_id() -> str       새 논리적 실행 시작 시 cli가 1회 호출(발급 지점)
    - build_evidence(skill_ref, verification, run_id, demo_seed, reuser_alias) -> ReuseEvidence
    - record_actual_reuse(evidence) -> RecordResult   (카운트 + 공유 이벤트 생성)
    - current_count(id, version) -> int
    - export_shared_usage() -> bytes                  (C-d: VERIFIED_REUSE 이벤트만)
    - import_shared_usage(blob, local_ref_exists) -> list  (C-d: 재검증·event_id dedup)

규칙(R3, 정합화 1·2):
    - 카운트 증가는 오직 record_actual_reuse. store.put(C2)은 절대 카운트 변경 없음.
    - counted=True ⟺ is_real_success & !demo_seed & run_id 미기록(새 실행).
    - 동일 run_id 재기록(재검증/재시도/재시작) → counted=False, reason="same-execution".
    - run_id는 '실행'을 식별. 같은 문제의 다른 환경 재사용은 새 run_id → 각각 +1.
    - run_id 발급은 new_execution_id뿐. S1/검증은 발급하지 않고 전달만 받는다.

C-d(공유 재사용 이벤트, VERIFIED_REUSE):
    - 이벤트는 counted=True & 정확한 Skill 참조(digest 포함)가 있을 때만 생성.
      exact Skill 참조({id,version,digest})와 reuser_alias는 **호출자(cli/S1 경로)가 제공**한다.
    - event_id는 (id,version,digest,run_id,reuser_alias)의 결정적 파생 → export/import/재전송
      시 동일 이벤트는 같은 event_id를 유지. 이미 반영한 event_id는 재집계하지 않는다(dedup).
    - **기존 counts에서 과거 이벤트·성공 근거를 역산해 만들지 않는다**(이 계약 도입 이후 실제
      성공에서만 이벤트가 생성됨).
    - import_shared_usage는 counts를 바꾸지 않는다(로컬 재사용 카운트는 로컬 전용). 조직 실적은
      검증·dedup을 통과한 events로 집계한다.
저장: 로컬 JSON. {counts, seen_run_ids, events} — seen_run_ids로 실행 dedup, events는 event_id dedup.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

_KEYSEP = "\x1f"


@dataclass
class ReuseEvidence:
    skill_ref: dict              # {id, version[, digest]} — 어떤 Skill을 재사용했는지
    is_real_success: bool        # clean+pip 종료코드+설치·버전+import 검증 통과 여부
    verification: dict           # 검증 방법·결과 상세
    run_id: str                  # 안정적 실행 식별자(호출자 발급, 전달만)
    demo_seed: bool = False       # 미리 만든 실적이면 True(실적 카운트·이벤트 제외)
    reuser_alias: str = "local"  # 재사용 주체 별칭(비민감; 이벤트 생성 시 호출자 제공)
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


def compute_event_id(skill_ref: dict, run_id: str, reuser_alias: str) -> str:
    """공유 재사용 이벤트의 결정적 식별자.

    (id, version, digest, run_id, reuser_alias)로 파생 → 같은 실제 재사용 이벤트는
    export/import/재전송을 거쳐도 동일 event_id를 유지(왕복 dedup 키).
    """
    canonical = _KEYSEP.join([
        skill_ref.get("id", ""),
        skill_ref.get("version", ""),
        skill_ref.get("digest", ""),
        run_id,
        reuser_alias,
    ])
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_evidence(skill_ref: dict, verification: dict, run_id: str,
                   demo_seed: bool = False, reuser_alias: str = "local") -> ReuseEvidence:
    """검증 결과로부터 ReuseEvidence 구성. run_id는 호출자가 전달(재발급 없음).

    공유 이벤트를 만들려면 skill_ref에 정확한 digest가 포함되어야 하며, reuser_alias도
    호출자가 제공한다. digest가 없으면 카운트는 되지만 이벤트는 생성되지 않는다.
    """
    return ReuseEvidence(
        skill_ref=dict(skill_ref),
        is_real_success=bool(verification.get("is_real_success", False)),
        verification=dict(verification),
        run_id=run_id,
        demo_seed=demo_seed,
        reuser_alias=reuser_alias,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


class UsageTracker:
    """카운트·seen_run_ids·공유 이벤트를 로컬 JSON에 영속화. 카운트 쓰기의 유일 경로."""

    def __init__(self, path: str):
        self.path = path
        self._counts: dict[str, int] = {}
        self._seen: set[str] = set()
        self._events: dict[str, dict] = {}   # event_id -> 이벤트 레코드
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._counts = data.get("counts", {})
            self._seen = set(data.get("seen_run_ids", []))
            self._events = data.get("events", {})  # 하위호환: 없으면 빈 dict

    def _save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "counts": self._counts,
                    "seen_run_ids": sorted(self._seen),
                    "events": self._events,
                },
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
        # C-d: counted=True & 정확한 Skill 참조(digest)가 있을 때만 공유 이벤트 생성.
        if evidence.skill_ref.get("digest"):
            self._record_shared_event(evidence)
        self._save()
        return RecordResult(True, self._counts[key], reason="ok")

    def _record_shared_event(self, evidence: ReuseEvidence) -> None:
        eid = compute_event_id(evidence.skill_ref, evidence.run_id, evidence.reuser_alias)
        # 이미 있는 event_id면 그대로(재집계 없음).
        self._events.setdefault(eid, {
            "event_id": eid,
            "skill_ref": {
                "id": evidence.skill_ref["id"],
                "version": evidence.skill_ref["version"],
                "digest": evidence.skill_ref["digest"],
            },
            "reuser_alias": evidence.reuser_alias,
            "evidence": {
                "is_real_success": True,
                "verification": dict(evidence.verification),
            },
            "demo_seed": False,
            "timestamp": evidence.timestamp,
        })

    def current_count(self, id: str, version: str) -> int:
        return self._counts.get(_key(id, version), 0)

    def seed_count(self, id: str, version: str, count: int) -> None:
        """DEMO_SEED(미리 만든 실적) 주입 — 실제 재사용 경로와 분리된 시연용."""
        self._counts[_key(id, version)] = count
        self._save()

    # --- C-d: 공유 재사용 이벤트 export/import (VERIFIED_REUSE) ---

    def export_shared_usage(self) -> bytes:
        """VERIFIED_REUSE 자격 이벤트만 직렬화. counts 원본·seen_run_ids·로컬 DB는 전송 안 함.

        이벤트는 생성 시점에 이미 실제 성공·비-DEMO만 기록되므로 자격을 만족한다(재확인 필터 포함).
        """
        events = [
            ev for ev in self._events.values()
            if ev.get("evidence", {}).get("is_real_success") and not ev.get("demo_seed")
        ]
        return json.dumps(
            {"events": events}, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")

    def import_shared_usage(self, blob: bytes, local_ref_exists=None) -> list[dict]:
        """수신 이벤트를 재검증·event_id dedup 후 반영. counts는 바꾸지 않는다(조직 실적=events).

        local_ref_exists(skill_ref{id,version,digest}) -> bool: 정확한 Skill이 로컬에 존재하는지
        확인하는 콜러블(cli/gitsync가 제공). VERIFIED_REUSE = 로컬 존재 + 실제 성공 + 비-DEMO.
        """
        data = json.loads(blob.decode("utf-8"))
        results: list[dict] = []
        changed = False
        for ev in data.get("events", []):
            eid = ev.get("event_id", "")
            if eid in self._events:
                # 이미 반영한 이벤트(자기 이벤트가 왕복해 돌아온 경우 포함) → 재집계 안 함.
                results.append({"event_id": eid, "applied": False, "reason": "dedup"})
                continue
            if not (ev.get("evidence", {}).get("is_real_success") and not ev.get("demo_seed")):
                results.append({"event_id": eid, "applied": False, "reason": "not-verified"})
                continue
            ref = ev.get("skill_ref", {})
            if local_ref_exists is not None and not local_ref_exists(ref):
                results.append({"event_id": eid, "applied": False, "reason": "not-local"})
                continue
            self._events[eid] = ev
            changed = True
            results.append({"event_id": eid, "applied": True, "reason": "ok"})
        if changed:
            self._save()
        return results

    def shared_reuse_count(self, id: str, version: str) -> int:
        """해당 Skill의 공유 이벤트 수(조직 실적 집계용, event_id dedup 기준)."""
        return sum(
            1 for ev in self._events.values()
            if ev.get("skill_ref", {}).get("id") == id
            and ev.get("skill_ref", {}).get("version") == version
        )

    def list_shared_events(self) -> list[dict]:
        return [ev for ev in self._events.values()]


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
