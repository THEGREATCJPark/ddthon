"""C2 — SkillStore: 로컬 JSON 저장·조회·dedup·CONFLICT. 카운트 미기록.

소유(단일 수정자): CJ
계약(Code Plan §1 + U2 공통 의존성 C-a/C-b):
    - get(id, version) -> Descriptor | None
    - list() -> list[Descriptor]
    - put(d) -> PutResult   result: "STORED"|"DEDUP"|"CONFLICT"
    - export_bundle(refs) -> bytes          (C-b: S3 판정 허용목록만·content만)
    - import_bundle(blob) -> list[PutResult] (C-b: digest 재계산·DEDUP/CONFLICT·content만)
    - save_lifecycle_state / load_lifecycle_state / list_lifecycle_records (C-a: 저장만)

규칙(R2):
    - CONFLICT = 동일 (id, version) + 다른 digest. 다른 version은 CONFLICT 아님.
    - DEDUP = 동일 (id, version) + 동일 digest → no-op. usage 병합·actual_reuse 변경 없음.
    - store.put은 절대 usage/카운트를 변경하지 않는다(카운트 쓰기는 C3 단독).

C-a(lifecycle 저장): S3(B)가 상태 전이를 판단, C2(CJ)는 전달받은 상태를 저장·로드만.
    - 전이 규칙·게이트는 C2가 판단하지 않는다. 상태·근거는 정확한 candidate의
      (id, version, digest)에 연결. 외부 소비자는 S3 조회 계약으로만 상태를 읽는다.
C-b(descriptor 공유): export는 S3가 공유 가능하다고 판정한 정확한 candidate refs만 대상.
    - 단순 scope 플래그로 전체 항목을 내보내지 않는다(명시적 refs 허용목록).
    - export/import 양측 모두 content로 digest 재계산 → 선언 digest 불일치는 제외/거부.
    - content(불변부)만 전송·반영. 원격 문자열로 로컬 승인/Replay를 만들지 않는다.

저장: 로컬 JSON. skills 키 = "id\x1fversion". lifecycle 키 = "id\x1fversion\x1fdigest".
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone

from . import descriptor as _d
from .descriptor import CONTENT_KEYS, Descriptor

_KEYSEP = "\x1f"


@dataclass
class PutResult:
    result: str          # "STORED" | "DEDUP" | "CONFLICT"
    reason: str = ""


def _key(id: str, version: str) -> str:
    return f"{id}{_KEYSEP}{version}"


def _lkey(id: str, version: str, digest: str) -> str:
    return f"{id}{_KEYSEP}{version}{_KEYSEP}{digest}"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class SkillStore:
    """로컬 JSON 파일 기반 Skill 저장소. 카운트/usage는 여기서 쓰지 않는다."""

    def __init__(self, path: str):
        self.path = path
        self._skills: dict[str, dict] = {}
        self._lifecycle: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._skills = data.get("skills", {})
            self._lifecycle = data.get("lifecycle", {})  # 하위호환: 없으면 빈 dict
        else:
            self._skills = {}
            self._lifecycle = {}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                {"skills": self._skills, "lifecycle": self._lifecycle},
                f, ensure_ascii=False, sort_keys=True,
            )
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

    # --- C-b: descriptor 공유 export/import (content만) ---

    def export_bundle(self, refs: list[dict]) -> bytes:
        """S3가 공유 가능하다고 판정한 **정확한 candidate refs만** content로 내보낸다.

        refs = [{id, version, digest}, ...] — 허용목록(전체 export 아님).
        각 ref에 대해 로컬 저장본을 조회하고, content로 digest를 **재계산**해
        선언 digest와 로컬 저장 digest가 모두 일치할 때만 포함한다(위조·불일치 제외).
        usage/카운트/lifecycle은 포함하지 않는다(content 불변부만).
        """
        out: list[dict] = []
        for ref in refs:
            rid, rver, rdig = ref.get("id"), ref.get("version"), ref.get("digest")
            if not (rid and rver and rdig):
                continue  # 정확한 참조(id/version/digest) 아님 → 제외
            d = self.get(rid, rver)
            if d is None:
                continue  # 로컬 미존재 → 제외
            content = {k: getattr(d, k) for k in CONTENT_KEYS}
            recomputed = _d.compute_digest(content)
            # 판정 대상(ref) ↔ export 대상(로컬)의 id/version/digest 일치 확인
            if not (d.digest == rdig == recomputed):
                continue  # digest 불일치 → 제외(무결성·정확성 보장)
            out.append({"content": content, "declared_digest": rdig})
        return json.dumps(
            {"skills": out}, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")

    def import_bundle(self, blob: bytes) -> list[PutResult]:
        """content만 역직렬화 → digest 재계산·검증 → put 규칙(DEDUP/CONFLICT) 반영.

        원격 문자열로 로컬 승인·Replay 기록을 만들지 않는다(저장만).
        선언 digest와 content 재계산 digest가 다르면 거부(위조 방지).
        """
        data = json.loads(blob.decode("utf-8"))
        results: list[PutResult] = []
        for item in data.get("skills", []):
            content = item.get("content", {})
            declared = item.get("declared_digest", "")
            if not all(k in content for k in CONTENT_KEYS):
                results.append(PutResult("CONFLICT", reason="missing content keys"))
                continue
            recomputed = _d.compute_digest(content)
            if recomputed != declared:
                # 선언 digest 위조·손상 → 반영 거부
                results.append(PutResult("CONFLICT", reason="digest mismatch (import)"))
                continue
            d = _d.make_descriptor(content)  # usage 없음: actual_reuse=0, demo_seed=False
            results.append(self.put(d))
        return results

    # --- C-a: lifecycle 상태 저장·로드 (저장만, 전이 미판단) ---

    def save_lifecycle_state(self, skill_ref: dict, state: str, evidence: dict) -> None:
        """S3(B)가 판정한 lifecycle 상태를 그대로 영속한다.

        C2는 전이 규칙·게이트를 판단·검증하지 않는다(저장만). 상태·근거는
        정확한 candidate의 (id, version, digest)에 연결한다.
        """
        rid, rver, rdig = skill_ref["id"], skill_ref["version"], skill_ref["digest"]
        self._lifecycle[_lkey(rid, rver, rdig)] = {
            "id": rid, "version": rver, "digest": rdig,
            "state": state, "evidence": dict(evidence), "updated_at": _now(),
        }
        self._save()

    def load_lifecycle_state(self, skill_ref: dict) -> dict | None:
        return self._lifecycle.get(
            _lkey(skill_ref["id"], skill_ref["version"], skill_ref["digest"])
        )

    def list_lifecycle_records(self) -> list[dict]:
        # 모듈 레벨 list() 편의 함수가 내장 list를 가리므로 컴프리헨션 사용.
        return [rec for rec in self._lifecycle.values()]


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
