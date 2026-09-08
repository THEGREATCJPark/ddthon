"""S1 — ReuseService: 시나리오 비의존 적용 + 실제 효과 검증 + 실제 성공 판정.

소유(단일 수정자): A (최호길) — 이 파일은 A만 편집. 인계 후 CJ 동시 수정 금지.
계약(Code Plan §1, §3):
    - apply_and_verify(selected, obs, env, run_id) -> ApplicationResult | FileAccessResult

규칙(RU2, 정정 Q3·정합화 2·3):
    - run_id는 호출자(cli)가 발급해 전달 — S1 내부 재발급 금지(재시도 시 동일 run_id 수신).
    - "실제 성공" = 실제 실행·검증 통과. 성공 index/절차 선택 자체는 성공 근거 아님.

P1 확장(승인 2026-09-08, CJ/B 계약):
    - procedure.action 으로 파일접근 경로 분기(기존 pip-install 경로/동작 보존).
    - B 제공 계약: run_file_access_procedure(procedure, env) -> {ok, content, method, evidence}
      (모듈 경로·시그니처 확정 전까지 late-bind; 준비/테스트는 file_access_runner 대역 주입).
    - S1은 B의 접근 실행 결과를 검증하고 로컬 artifact_ref·근거만 반환.
      업무 원문(raw content)은 결과/공유 이벤트에 직접 싣지 않는다(로컬 참조화).
    - P0의 '패키지 미설치 clean' 전제는 파일접근에 그대로 적용하지 않는다.
CJ 소유 계약(envharness_p0)은 호출만.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass

from . import envharness_p0 as harness

# procedure.action 식별자. P0=pip-install(기본, 동작 보존), P1=file-access.
ACTION_PIP_INSTALL = "pip-install"
ACTION_FILE_ACCESS = "file-access"


@dataclass
class ApplicationResult:
    """P0(pip) 결과 — 필드/의미 불변(인계본 보존)."""
    pip_exit_code: int
    installed_check: bool
    version_check: bool
    import_check: bool
    index_source: str
    is_real_success: bool
    run_id: str


@dataclass
class FileAccessResult:
    """P1(file-access) 결과 — S1이 접근 효과를 검증하고 로컬 참조/근거만 반환.

    주의: 업무 원문(raw content)은 담지 않는다. 획득 내용은 로컬 artifact로 저장하고
    artifact_ref(참조)만 반환한다(공유 Skill/이벤트에 원문 미포함).
    """
    is_real_success: bool
    run_id: str
    action: str
    access_ok: bool
    access_method: str | None
    access_evidence: object
    artifact_ref: str | None


# --------------------------------------------------------------------------- #
# P0 (pip-install) — 기존 경로. 동작/검증 로직 불변.
# --------------------------------------------------------------------------- #
def _pip_install(env, index_dir: str, target: str) -> int:
    """절차가 지정한 로컬 index로 실제 pip 설치를 수행하고 종료코드를 반환."""
    proc = subprocess.run(
        [env.python_exe, "-m", "pip", "install",
         "--no-index", "--find-links", index_dir, target],
        capture_output=True, text=True,
    )
    return proc.returncode


def _verify_installed(env, target: str) -> tuple[bool, bool]:
    """pip show로 설치 여부와 요구 버전(TARGET_VERSION) 일치를 확인.

    반환: (installed_check, version_check).
    """
    proc = subprocess.run(
        [env.python_exe, "-m", "pip", "show", target],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return False, False
    installed_version = None
    for line in proc.stdout.splitlines():
        if line.lower().startswith("version:"):
            installed_version = line.split(":", 1)[1].strip()
            break
    return True, installed_version == harness.TARGET_VERSION


def _verify_import(env) -> bool:
    """격리 환경에서 합성 패키지 import 성공 여부를 확인."""
    proc = subprocess.run(
        [env.python_exe, "-c", f"import {harness.TARGET_IMPORT}"],
        capture_output=True, text=True,
    )
    return proc.returncode == 0


def _apply_pip_install(selected, obs, env, run_id: str) -> ApplicationResult:
    """P0: 선택 절차를 clean 환경에 적용하고 실제 설치·효과를 검증(동작 불변).

    "실제 성공" = clean 전제 + pip 종료코드 0 + 설치·요구버전 일치 + 합성 import 성공.
    검증의 요구버전·import는 P0 합성 대상(harness.TARGET_VERSION/TARGET_IMPORT) 기준(P1 일반화 지점).
    """
    # 오판 방지: 전역/기존 설치로 인한 거짓 성공 배제.
    # assert가 아닌 명시적 raise — python -O에서도 정직성 전제(가짜 성공 금지)가 유지되어야 함.
    if not harness.is_clean(env, obs.target_pkg):
        raise RuntimeError("clean 환경 전제 위반: 대상 패키지가 이미 설치됨(오판 방지)")

    cfg = selected.procedure
    index_name = cfg["index"]
    target = cfg.get("target", obs.target_pkg)
    index_dir = harness.resolve_index(index_name)

    pip_exit_code = _pip_install(env, index_dir, target)
    installed_check, version_check = _verify_installed(env, target)
    import_check = _verify_import(env)

    is_real_success = (
        pip_exit_code == 0 and installed_check and version_check and import_check
    )
    return ApplicationResult(
        pip_exit_code=pip_exit_code,
        installed_check=installed_check,
        version_check=version_check,
        import_check=import_check,
        index_source=index_name,
        is_real_success=is_real_success,
        run_id=run_id,
    )


# --------------------------------------------------------------------------- #
# P1 (file-access) — B 실행 결과 검증 + 로컬 참조/근거 반환.
# --------------------------------------------------------------------------- #
def _default_file_access_runner(procedure, env):
    """B 소유 실행 함수(run_file_access_procedure)로 위임.

    모듈 경로·시그니처 확정 전까지 미연결 — 호출 시 NotImplementedError.
    (준비/테스트 단계에서는 apply_and_verify(file_access_runner=대역)로 주입한다.
     이 경로로 들어온 '실제 연결' 성공과 대역 테스트 결과는 명확히 구분된다.)
    """
    try:
        from .file_access import run_file_access_procedure  # B 제공 예정(경로 확정 시 조정)
    except ImportError as exc:
        raise NotImplementedError(
            "run_file_access_procedure 미연결: B의 실제 모듈 경로·시그니처 확정 후 연결. "
            "그 전까지 file_access_runner 대역을 주입하세요."
        ) from exc
    return run_file_access_procedure(procedure, env)


def _persist_artifact(content, run_id: str) -> str:
    """획득 내용을 로컬 임시 파일로 저장하고 참조(경로)만 반환.

    업무 원문을 결과/공유 이벤트에 직접 싣지 않기 위한 로컬 참조화.
    """
    data = content if isinstance(content, (bytes, bytearray)) else str(content).encode("utf-8")
    fd, path = tempfile.mkstemp(prefix=f"skillloop-artifact-{run_id}-", suffix=".bin")
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return path


def _apply_file_access(selected, obs, env, run_id: str, file_access_runner) -> FileAccessResult:
    """B의 파일접근 실행 결과를 검증하고 로컬 artifact_ref·근거를 반환(S1).

    B 계약: run_file_access_procedure(procedure, env) -> {ok, content, method, evidence}
    "실제 성공"(is_real_success) = 접근 ok + 검증 근거 존재 + 획득 내용의 로컬 artifact 확보.
    획득 내용 자체는 로컬 artifact로만 남기고 참조(artifact_ref)를 반환한다(원문 미노출).
    """
    runner = file_access_runner or _default_file_access_runner
    outcome = runner(selected.procedure, env)

    access_ok = bool(outcome.get("ok"))
    method = outcome.get("method")
    evidence = outcome.get("evidence")
    content = outcome.get("content")

    artifact_ref = None
    if access_ok and content is not None:
        artifact_ref = _persist_artifact(content, run_id)

    is_real_success = access_ok and evidence is not None and artifact_ref is not None
    return FileAccessResult(
        is_real_success=is_real_success,
        run_id=run_id,
        action=ACTION_FILE_ACCESS,
        access_ok=access_ok,
        access_method=method,
        access_evidence=evidence,
        artifact_ref=artifact_ref,
    )


def apply_and_verify(selected, obs, env, run_id: str, *, file_access_runner=None):
    """선택된 Skill 절차를 적용하고 실제 효과를 검증. run_id는 전달만(재발급 금지).

    procedure.action 으로 경로 분기:
      - "file-access" → 파일접근 검증 경로(FileAccessResult) [P1]
      - 그 외(기존 pip-install 포함) → pip 설치·검증 경로(ApplicationResult) [P0, 동작 불변]
    file_access_runner: B의 run_file_access_procedure 대역 주입점.
      미지정 시 실제 모듈을 late-import(미확정이면 NotImplementedError → 대역과 구분됨).
    """
    action = selected.procedure.get("action")
    if action == ACTION_FILE_ACCESS:
        return _apply_file_access(selected, obs, env, run_id, file_access_runner)
    return _apply_pip_install(selected, obs, env, run_id)
