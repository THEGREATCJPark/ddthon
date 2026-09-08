"""V7, V8 — 실제 성공 정의·index 비강제. 소유: A. 구현: S8."""

import shutil

import pytest

from skillloop import descriptor as D
from skillloop import envharness_p0 as H
from skillloop import match as M
from skillloop import reuse_service as RS


def _obs():
    return M.FailureObservation(
        command=f"pip install {H.TARGET_PKG}",
        target_pkg=H.TARGET_PKG,
        error_signature=f"pip-install-fail:{H.TARGET_PKG}",
        exit_code=1,
    )


def _skill(index, target=H.TARGET_PKG):
    content = {
        "id": "fix-skillloop-demo-pkg-install",
        "version": "1.0.0",
        "origin": {"author": "seed"},
        "applicability": {"signals": [f"pip-install-fail:{H.TARGET_PKG}"]},
        "procedure": {"action": "pip-install", "index": index, "target": target},
    }
    return D.make_descriptor(content)


@pytest.fixture
def clean_env():
    H.prepare()                       # failing/allow 로컬 index 준비(오프라인 wheel 빌드)
    env = H.make_clean_venv()         # 실행마다 격리 clean venv
    try:
        yield env
    finally:
        shutil.rmtree(env.venv_path, ignore_errors=True)


def test_real_success_requires_clean_install_version_import(clean_env):
    # 실제 성공 = clean 전제 + pip exit0 + 설치·요구버전 + 합성 import 모두 충족.
    res = RS.apply_and_verify(_skill("allow"), _obs(), clean_env, run_id="run-success")

    assert res.pip_exit_code == 0
    assert res.installed_check is True
    assert res.version_check is True
    assert res.import_check is True
    assert res.is_real_success is True
    # is_real_success는 네 조건의 AND로만 성립.
    assert res.is_real_success == (
        res.pip_exit_code == 0
        and res.installed_check
        and res.version_check
        and res.import_check
    )
    # run_id는 전달만(재발급 금지).
    assert res.run_id == "run-success"
    assert res.index_source == "allow"


def test_index_selection_alone_is_not_success(clean_env):
    # 정답 index(allow)를 '선택'했더라도 실제 설치·검증이 안 되면 성공이 아니다.
    skill = _skill("allow", target="skillloop-nonexistent-pkg")
    res = RS.apply_and_verify(skill, _obs(), clean_env, run_id="run-select-only")

    assert res.index_source == "allow"          # 성공 index를 선택함
    assert res.pip_exit_code != 0               # 그러나 실제 설치는 실패
    assert res.installed_check is False
    assert res.import_check is False
    assert res.is_real_success is False          # 선택 사실만으로는 성공 아님
