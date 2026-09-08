"""V3, V4 — CONFLICT 판정·DEDUP 카운트 무변경. 소유: CJ. 구현: S3."""

import pytest

pytestmark = pytest.mark.skip(reason="stub — S3 미구현 (PASS 아님)")


def test_conflict_same_id_version_different_digest():
    raise NotImplementedError("S3")


def test_dedup_does_not_change_usage_or_count():
    raise NotImplementedError("S3")
