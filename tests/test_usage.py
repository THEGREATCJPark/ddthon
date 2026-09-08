"""V9, V10, V11 — C3 단독 카운트·run_id 실행 dedup·사전적재 실적 반영. 소유: CJ. 구현: S4."""

import pytest

pytestmark = pytest.mark.skip(reason="stub — S4 미구현 (PASS 아님)")


def test_only_real_success_increments_count():
    raise NotImplementedError("S4")


def test_same_run_id_does_not_double_count():
    raise NotImplementedError("S4")


def test_preloaded_skill_reuse_counts_when_not_demo_seed():
    raise NotImplementedError("S4")
