"""C1 — SkillDescriptor: 불변 content + 가변 usage, canonical 직렬화·SHA-256 digest.

소유(단일 수정자): CJ
계약(Code Plan §1):
    - canonical_json(content_wo_digest) -> bytes  (키 정렬·정규화)
    - compute_digest(content_wo_digest) -> str    (sha256 hex, digest·usage 제외)
    - serialize(d) -> bytes                        (canonical)
    - deserialize(b) -> Descriptor                 (round-trip 동일 digest)

digest 규칙(R1): 불변 content {id, version, origin, applicability, procedure}에
대해서만 계산. digest 필드 자체와 가변 usage(actual_reuse, demo_seed)는 제외.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


# 불변 content 키(해시 입력 대상). digest·usage 제외.
CONTENT_KEYS = ("id", "version", "origin", "applicability", "procedure")


@dataclass(frozen=True)
class Descriptor:
    id: str
    version: str
    digest: str
    origin: dict
    applicability: dict
    procedure: dict
    actual_reuse: int = 0      # 가변 usage
    demo_seed: bool = False    # 가변 usage (미리 만든 실적 표식)


def _content_of(d: Descriptor) -> dict:
    """Descriptor에서 digest·usage를 제외한 불변 content dict 추출."""
    return {k: getattr(d, k) for k in CONTENT_KEYS}


def canonical_json(content_wo_digest: dict) -> bytes:
    """불변 content를 키 정렬·정규화한 canonical JSON 바이트로 직렬화.

    - 키 정렬(sort_keys) + 공백 제거(compact separators)로 표현을 정규화.
    - UTF-8 고정, ensure_ascii=False로 유니코드 정규 표현 유지.
    digest·usage 필드가 섞여 들어오더라도 CONTENT_KEYS만 사용해 해시 입력을 고정.
    """
    content = {k: content_wo_digest[k] for k in CONTENT_KEYS if k in content_wo_digest}
    return json.dumps(
        content, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def compute_digest(content_wo_digest: dict) -> str:
    """canonical_json 위에서 SHA-256 hex digest를 계산(digest·usage 제외)."""
    return hashlib.sha256(canonical_json(content_wo_digest)).hexdigest()


def make_descriptor(content: dict, actual_reuse: int = 0, demo_seed: bool = False) -> Descriptor:
    """불변 content로부터 digest를 계산해 Descriptor를 생성하는 편의 함수."""
    digest = compute_digest(content)
    return Descriptor(
        id=content["id"],
        version=content["version"],
        digest=digest,
        origin=content["origin"],
        applicability=content["applicability"],
        procedure=content["procedure"],
        actual_reuse=actual_reuse,
        demo_seed=demo_seed,
    )


def serialize(d: Descriptor) -> bytes:
    """Descriptor를 canonical 바이트로 직렬화(저장·전송용). digest·usage 포함."""
    payload = {
        "id": d.id,
        "version": d.version,
        "digest": d.digest,
        "origin": d.origin,
        "applicability": d.applicability,
        "procedure": d.procedure,
        "actual_reuse": d.actual_reuse,
        "demo_seed": d.demo_seed,
    }
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def deserialize(b: bytes) -> Descriptor:
    """canonical 바이트에서 Descriptor 복원. round-trip 후 digest 동일 보장."""
    obj = json.loads(b.decode("utf-8"))
    return Descriptor(
        id=obj["id"],
        version=obj["version"],
        digest=obj["digest"],
        origin=obj["origin"],
        applicability=obj["applicability"],
        procedure=obj["procedure"],
        actual_reuse=obj.get("actual_reuse", 0),
        demo_seed=obj.get("demo_seed", False),
    )
