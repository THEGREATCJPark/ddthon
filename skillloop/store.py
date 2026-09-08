"""C2 — SkillStore: 로컬 JSON 저장·조회·dedup·CONFLICT. 카운트 미기록.

소유(단일 수정자): CJ
계약(Code Plan §1):
    - get(id, version) -> Descriptor | None
    - list() -> list[Descriptor]
    - put(d) -> PutResult   result: "STORED"|"DEDUP"|"CONFLICT"

규칙(R2):
    - CONFLICT = 동일 (id, version) + 다른 digest. 다른 version은 CONFLICT 아님.
    - DEDUP = 동일 (id, version) + 동일 digest → no-op. usage 병합·actual_reuse 변경 없음.
    - store.put은 절대 usage/카운트를 변경하지 않는다(카운트 쓰기는 C3 단독).
"""

from __future__ import annotations

from dataclasses import dataclass

from .descriptor import Descriptor


@dataclass
class PutResult:
    result: str          # "STORED" | "DEDUP" | "CONFLICT"
    reason: str = ""


def get(id: str, version: str) -> Descriptor | None:
    """(id, version) 키로 저장된 Descriptor 조회. 없으면 None."""
    raise NotImplementedError("S3")


def list() -> list[Descriptor]:
    """저장된 모든 Descriptor 목록."""
    raise NotImplementedError("S3")


def put(d: Descriptor) -> PutResult:
    """저장 시도. STORED/DEDUP/CONFLICT 판정. usage·카운트는 변경하지 않음."""
    raise NotImplementedError("S3")
