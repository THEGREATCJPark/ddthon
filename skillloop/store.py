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

저장: 로컬 JSON 파일. 키 = "id\x1fversion".
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from . import descriptor as _d
from .descriptor import Descriptor

_KEYSEP = "\x1f"


@dataclass
class PutResult:
    result: str          # "STORED" | "DEDUP" | "CONFLICT"
    reason: str = ""


def _key(id: str, version: str) -> str:
    return f"{id}{_KEYSEP}{version}"


class SkillStore:
    """로컬 JSON 파일 기반 Skill 저장소. 카운트/usage는 여기서 쓰지 않는다."""

    def __init__(self, path: str):
        self.path = path
        self._skills: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._skills = data.get("skills", {})
        else:
            self._skills = {}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"skills": self._skills}, f, ensure_ascii=False, sort_keys=True)
        os.replace(tmp, self.path)

    def get(self, id: str, version: str) -> Descriptor | None:
        raw = self._skills.get(_key(id, version))
        if raw is None:
            return None
        return _d.deserialize(json.dumps(raw).encode("utf-8"))

    def list(self) -> list[Descriptor]:
        return [
            _d.deserialize(json.dumps(raw).encode("utf-8"))
            for raw in self._skills.values()
        ]

    def put(self, d: Descriptor) -> PutResult:
        existing = self.get(d.id, d.version)
        if existing is None:
            self._skills[_key(d.id, d.version)] = json.loads(_d.serialize(d).decode("utf-8"))
            self._save()
            return PutResult("STORED")
        if existing.digest == d.digest:
            # DEDUP: no-op. usage 병합·카운트 변경 없음(기존 레코드 그대로 유지).
            return PutResult("DEDUP", reason="same (id,version) + same digest")
        # 동일 (id, version) + 다른 digest → CONFLICT. 덮어쓰지 않고 거부.
        return PutResult("CONFLICT", reason="same (id,version) + different digest")


# --- 프로세스 기본 저장소(모듈 레벨 편의 함수) ---
_DEFAULT_PATH = os.environ.get(
    "SKILLLOOP_STORE", os.path.join(os.path.expanduser("~"), ".skillloop", "store.json")
)
_default: SkillStore | None = None


def _default_store() -> SkillStore:
    global _default
    if _default is None:
        _default = SkillStore(_DEFAULT_PATH)
    return _default


def get(id: str, version: str) -> Descriptor | None:
    return _default_store().get(id, version)


def list() -> list[Descriptor]:
    return _default_store().list()


def put(d: Descriptor) -> PutResult:
    return _default_store().put(d)
