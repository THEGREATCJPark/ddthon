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
# P1 — file-access 분기. B(1760d32) 실제 반환형 AccessResult + evidence 근거로 재검증.
# --------------------------------------------------------------------------- #
# 대역은 dict가 아니라 B의 실제 반환형(AccessResult)을 사용한다. B 모듈이 통합돼 있으면
# 실제 클래스를, 아직 이 브랜치에 없으면 동일 필드의 충실 대역을 사용(반환형 일치).
try:  # pragma: no cover - 통합 여부에 따라 분기
    from skillloop.envharness_p1 import AccessResult
except Exception:  # 미통합 브랜치: B AccessResult와 동일 계약(ok/content/method/evidence)
    from dataclasses import dataclass, field

    @dataclass
    class AccessResult:  # mirror of skillloop.envharness_p1.AccessResult (B 1760d32)
        ok: bool
        content: object
        method: str
        evidence: dict = field(default_factory=dict)


# B의 실제 접근 성공 content 형태: [(month:str, total_output:int|float), ...] (완료월 3행).
_FA_CONTENT = [("2026-06", 1200), ("2026-07", 1350), ("2026-08", 1500)]
# B가 실제 성공 시 채우는 evidence(원본 무변경 + 최소형태 + read-only) 재현.
_FA_EVIDENCE_OK = {
    "original_unchanged": True,
    "completed_month_rows": True,
    "save_called": False,
    "sha256_before": "abc", "sha256_after": "abc",
}


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
        "procedure": {"action": "file-access", "sheet": 1, "month_col": 1, "total_col": 2},
    }
    return D.make_descriptor(content)


def _runner(access_result):
    """B의 run_file_access_procedure(procedure, env) 대역 — AccessResult를 반환한다."""
    def run(procedure, env):
        return access_result
    return run


def _cleanup(res):
    if res.artifact_ref and os.path.exists(res.artifact_ref):
        os.remove(res.artifact_ref)


def test_file_access_real_success_returns_artifact_ref_and_evidence():
    # 접근 ok + 원본 무변경·최소형태·read-only 근거 → is_real_success, 로컬 artifact 확보.
    runner = _runner(AccessResult(
        ok=True, content=_FA_CONTENT,
        method="excel-com-attach", evidence=dict(_FA_EVIDENCE_OK),
    ))
    res = RS.apply_and_verify(
        _fa_skill(), _fa_obs(), env=None, run_id="run-fa-ok",
        file_access_runner=runner,
    )
    try:
        assert res.action == "file-access"
        assert res.access_ok is True
        assert res.access_method == "excel-com-attach"
        assert res.access_evidence["original_unchanged"] is True
        assert res.is_real_success is True
        assert res.run_id == "run-fa-ok"            # run_id 전달만
        # 결과에는 참조만, 원문(업무 데이터)은 로컬 artifact 파일에만 존재.
        assert res.artifact_ref is not None
        assert os.path.exists(res.artifact_ref)
        with open(res.artifact_ref, "rb") as f:
            assert f.read() == str(_FA_CONTENT).encode("utf-8")
    finally:
        _cleanup(res)


def test_file_access_not_ok_is_not_success_and_no_artifact():
    # 접근 실패(ok=False, content=None, method="none") → 실제 성공 아님, artifact 없음.
    runner = _runner(AccessResult(
        ok=False, content=None, method="none",
        evidence={"error": "excel attach unavailable or not open", "save_called": False},
    ))
    res = RS.apply_and_verify(
        _fa_skill(), _fa_obs(), env=None, run_id="run-fa-fail",
        file_access_runner=runner,
    )
    assert res.access_ok is False
    assert res.is_real_success is False
    assert res.artifact_ref is None


def test_file_access_ok_but_no_unchanged_evidence_is_not_success():
    # ok·content가 있어도 원본 무변경 근거가 없으면(빈 근거) 성공 처리하지 않는다.
    runner = _runner(AccessResult(
        ok=True, content=_FA_CONTENT, method="excel-com-attach",
        evidence={"save_called": False},   # original_unchanged/completed_month_rows 없음
    ))
    res = RS.apply_and_verify(
        _fa_skill(), _fa_obs(), env=None, run_id="run-fa-noev",
        file_access_runner=runner,
    )
    try:
        assert res.access_ok is True
        assert res.is_real_success is False       # 근거 부족 → 성공 아님
        assert res.artifact_ref is None
    finally:
        _cleanup(res)


def test_file_access_changed_original_is_not_success():
    # 원본이 변경됐다는 근거(original_unchanged=False)면 성공 아님(실패 근거로 성공 금지).
    ev = dict(_FA_EVIDENCE_OK, original_unchanged=False)
    runner = _runner(AccessResult(
        ok=True, content=_FA_CONTENT, method="excel-com-attach", evidence=ev,
    ))
    res = RS.apply_and_verify(
        _fa_skill(), _fa_obs(), env=None, run_id="run-fa-changed",
        file_access_runner=runner,
    )
    try:
        assert res.is_real_success is False
        assert res.artifact_ref is None
    finally:
        _cleanup(res)


def test_file_access_save_called_breaks_read_only_success():
    # Save가 호출됐으면(read-only 위반) 성공 아님.
    ev = dict(_FA_EVIDENCE_OK, save_called=True)
    runner = _runner(AccessResult(
        ok=True, content=_FA_CONTENT, method="excel-com-attach", evidence=ev,
    ))
    res = RS.apply_and_verify(
        _fa_skill(), _fa_obs(), env=None, run_id="run-fa-saved",
        file_access_runner=runner,
    )
    try:
        assert res.is_real_success is False
        assert res.artifact_ref is None
    finally:
        _cleanup(res)


def test_unsupported_action_raises_not_pip():
    # 미지원 procedure.action은 pip 경로로 자동 실행하지 않고 명확히 거부한다.
    content = {
        "id": "weird-action-skill",
        "version": "1.0.0",
        "origin": {"author": "seed"},
        "applicability": {"signals": ["file-access-fail:encrypted-xlsx"]},
        "procedure": {"action": "run-shell", "cmd": "whatever"},
    }
    skill = D.make_descriptor(content)
    with pytest.raises(ValueError):
        RS.apply_and_verify(skill, _fa_obs(), env=None, run_id="run-bad-action")


def test_file_access_default_runner_not_wired_raises():
    # B 모듈(envharness_p1) 미통합이면 대역 미주입 시 late-import 실패로 NotImplementedError.
    # ('실제 연결' 미완료를 대역 결과와 명확히 구분: 조용한 성공 위장 금지.)
    # 통합 후에는 기본 runner가 실제 연결되므로(미연결 전제 소멸) 이 케이스는 해당 없음.
    import importlib.util

    if importlib.util.find_spec("skillloop.envharness_p1") is not None:
        pytest.skip("envharness_p1(B) 통합됨 — 기본 runner 실제 연결(미연결 대역 케이스 없음)")
    with pytest.raises(NotImplementedError):
        RS.apply_and_verify(_fa_skill(), _fa_obs(), env=None, run_id="run-fa-nowire")
