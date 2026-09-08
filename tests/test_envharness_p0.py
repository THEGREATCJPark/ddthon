"""envharness_p0 — 이중 mock index·격리 venv 준비(V7 전제). 소유: CJ. 구현: S5."""

import glob
import os
import shutil

import pytest

from skillloop import envharness_p0 as H


def test_prepare_builds_allow_wheel_and_failing_is_empty():
    H.prepare()
    allow = H.resolve_index("allow")
    failing = H.resolve_index("failing")
    # allow index에는 합성 패키지 wheel 존재
    assert glob.glob(os.path.join(allow, "skillloop_demo_pkg-*.whl"))
    # failing index에는 대상 패키지 없음
    assert not glob.glob(os.path.join(failing, "skillloop_demo_pkg-*.whl"))


def test_resolve_index_rejects_unknown():
    with pytest.raises(ValueError):
        H.resolve_index("nope")


@pytest.mark.slow
def test_clean_venv_is_clean_of_target():
    # V7 전제: 새 venv에는 대상 패키지가 없어야 함(전역 설치 오판 배제).
    env = H.make_clean_venv()
    try:
        assert os.path.exists(env.python_exe)
        assert H.is_clean(env, H.TARGET_PKG) is True
    finally:
        shutil.rmtree(env.venv_path, ignore_errors=True)
