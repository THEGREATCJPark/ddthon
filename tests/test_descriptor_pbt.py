"""V1, V2 — 직렬화 round-trip·digest 불변 (Hypothesis). 소유: CJ. 구현: S2."""

import pytest

pytestmark = pytest.mark.skip(reason="stub — S2 미구현 (PASS 아님)")


def test_serialize_roundtrip_preserves_digest():
    raise NotImplementedError("S2")


def test_digest_ignores_mutable_usage():
    raise NotImplementedError("S2")
