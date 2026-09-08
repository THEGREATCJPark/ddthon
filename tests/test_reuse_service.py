"""V7, V8 — 실제 성공 정의·index 비강제. 소유: A. 구현: S8."""

import pytest

pytestmark = pytest.mark.skip(reason="stub — S8 미구현 (PASS 아님)")


def test_real_success_requires_clean_install_version_import():
    raise NotImplementedError("S8")


def test_index_selection_alone_is_not_success():
    raise NotImplementedError("S8")
