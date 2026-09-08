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


def canonical_json(content_wo_digest: dict) -> bytes:
    """불변 content를 키 정렬·정규화한 canonical JSON 바이트로 직렬화."""
    raise NotImplementedError("S2")


def compute_digest(content_wo_digest: dict) -> str:
    """canonical_json 위에서 SHA-256 hex digest를 계산(digest·usage 제외)."""
    raise NotImplementedError("S2")


def serialize(d: Descriptor) -> bytes:
    """Descriptor를 canonical 바이트로 직렬화(저장·전송용)."""
    raise NotImplementedError("S2")


def deserialize(b: bytes) -> Descriptor:
    """canonical 바이트에서 Descriptor 복원. round-trip 후 digest 동일 보장."""
    raise NotImplementedError("S2")
