"""V5, V6 — 검색 결정성·다중후보 안정선택·오류 구분. 소유: A. 구현: S7."""

import pytest

pytestmark = pytest.mark.skip(reason="stub — S7 미구현 (PASS 아님)")


def test_multiple_valid_candidates_select_single_match():
    raise NotImplementedError("S7")


def test_no_match_only_when_zero_valid_candidates():
    raise NotImplementedError("S7")


def test_error_timeout_not_invoked_distinct_from_no_match():
    raise NotImplementedError("S7")
