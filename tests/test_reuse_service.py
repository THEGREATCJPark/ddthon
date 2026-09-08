"""V7, V8 — 실제 성공 정의·index 비강제. 소유: A. 구현: S8.

P1 확장(승인 2026-09-08): procedure.action="file-access" 분기, B 실행결과 검증 +
로컬 artifact_ref·근거 반환. B 실제 모듈 미확정 → 명시적 테스트 대역(runner)으로 검증.
'실제 연결'(late-import)은 미연결 시 NotImplementedError로 대역 결과와 구분된다.
"""

import os
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


# --------------------------------------------------------------------------- #
# P1 — file-access 분기(대역 기반). B 실행결과 검증 + 로컬 artifact_ref·근거.
# --------------------------------------------------------------------------- #
def _fa_obs():
    # P1: target_pkg는 호환용 대상 식별자(pip 명이 아님), 신호는 안정적 자원 유형 키.
    return M.FailureObservation(
        command="open encrypted-xlsx",
        target_pkg="encrypted-xlsx",
        error_signature="file-access-fail:encrypted-xlsx",
        exit_code=1,
    )


def _fa_skill():
    content = {
        "id": "fix-encrypted-xlsx-access",
        "version": "1.0.0",
        "origin": {"author": "seed"},
        "applicability": {"signals": ["file-access-fail:encrypted-xlsx"]},
        "procedure": {"action": "file-access", "resource": "encrypted-xlsx"},
    }
    return D.make_descriptor(content)


def _runner(outcome):
    """B의 run_file_access_procedure(procedure, env) 대역. 고정 결과 반환."""
    def run(procedure, env):
        return outcome
    return run


def test_file_access_real_success_returns_artifact_ref_and_evidence():
    # 접근 ok + 근거 + 획득 내용 → is_real_success, 로컬 artifact_ref 확보(원문 미노출).
    runner = _runner({
        "ok": True,
        "content": b"col_a,col_b\n1,2\n",
        "method": "user-open-excel-readonly",
        "evidence": {"rows": 2, "sheet": "Sheet1"},
    })
    res = RS.apply_and_verify(
        _fa_skill(), _fa_obs(), env=None, run_id="run-fa-ok",
        file_access_runner=runner,
    )
    try:
        assert res.action == "file-access"
        assert res.access_ok is True
        assert res.access_method == "user-open-excel-readonly"
        assert res.access_evidence == {"rows": 2, "sheet": "Sheet1"}
        assert res.is_real_success is True
        assert res.run_id == "run-fa-ok"           # run_id 전달만
        # 결과에는 참조만, 원문은 로컬 artifact 파일에만 존재.
        assert res.artifact_ref is not None
        assert os.path.exists(res.artifact_ref)
        with open(res.artifact_ref, "rb") as f:
            assert f.read() == b"col_a,col_b\n1,2\n"
    finally:
        if res.artifact_ref and os.path.exists(res.artifact_ref):
            os.remove(res.artifact_ref)


def test_file_access_not_ok_is_not_success_and_no_artifact():
    # 접근 실패(ok=False) → 실제 성공 아님, artifact_ref 없음(참조 미생성).
    runner = _runner({"ok": False, "content": None, "method": None, "evidence": None})
    res = RS.apply_and_verify(
        _fa_skill(), _fa_obs(), env=None, run_id="run-fa-fail",
        file_access_runner=runner,
    )
    assert res.access_ok is False
    assert res.is_real_success is False
    assert res.artifact_ref is None


def test_file_access_without_evidence_is_not_success():
    # 접근 ok·내용 있어도 검증 근거(evidence) 없으면 실제 성공 아님(가짜 성공 방지).
    runner = _runner({
        "ok": True,
        "content": b"data",
        "method": "user-open-excel-readonly",
        "evidence": None,
    })
    res = RS.apply_and_verify(
        _fa_skill(), _fa_obs(), env=None, run_id="run-fa-noev",
        file_access_runner=runner,
    )
    try:
        assert res.access_ok is True
        assert res.is_real_success is False       # 근거 없으면 성공 아님
    finally:
        if res.artifact_ref and os.path.exists(res.artifact_ref):
            os.remove(res.artifact_ref)


def test_file_access_default_runner_not_wired_raises():
    # B 실제 모듈 미확정 → 대역 미주입 시 late-import 실패로 NotImplementedError.
    # ('실제 연결' 미완료를 대역 결과와 명확히 구분: 조용한 성공 위장 금지.)
    with pytest.raises(NotImplementedError):
        RS.apply_and_verify(_fa_skill(), _fa_obs(), env=None, run_id="run-fa-nowire")
