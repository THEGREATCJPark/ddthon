"""V12 — run-p0 e2e 실제 샘플(실패→적용→검증→reuse+1). 소유: CJ 단일 수정자(A는 의견). 구현: S9."""

import pytest

pytestmark = pytest.mark.skip(reason="stub — S9 미구현 (PASS 아님)")


def test_run_p0_reuse_increments_to_one():
    raise NotImplementedError("S9")


def test_same_execution_reverify_keeps_count():
    raise NotImplementedError("S9")


def test_new_execution_increments_to_two():
    raise NotImplementedError("S9")
