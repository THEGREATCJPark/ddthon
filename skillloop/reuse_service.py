"""S1 — ReuseService: 시나리오 비의존 적용 + 실제 효과 검증 + 실제 성공 판정.

소유(단일 수정자): A (최호길) — 이 파일은 A만 편집. 인계 후 CJ 동시 수정 금지.
계약(Code Plan §1, §3):
    - apply_and_verify(selected, obs, env, run_id) -> ApplicationResult | FileAccessResult

규칙(RU2, 정정 Q3·정합화 2·3):
    - run_id는 호출자(cli)가 발급해 전달 — S1 내부 재발급 금지(재시도 시 동일 run_id 수신).
    - "실제 성공" = 실제 실행·검증 통과. 성공 index/절차 선택 자체는 성공 근거 아님.

P1 확장(승인 2026-09-08, CJ/B 계약 · B 기준 1760d32 정합):
    - procedure.action 으로 파일접근 경로 분기(기존 pip-install 경로/동작 보존).
    - B 제공 계약: skillloop.envharness_p1.run_file_access_procedure(procedure, env)
        -> AccessResult(ok: bool, content: list|None, method: str, evidence: dict)
      (모듈 확정: envharness_p1. 준비/테스트는 file_access_runner 대역 주입; 대역도 AccessResult형.)
    - S1은 B의 접근 실행 결과를 '재검증'한다: ok 플래그만 신뢰하지 않고 evidence의
      원본 무변경(original_unchanged) + 접근 최소형태(workbook_readable) +
      read-only(save_called=False)를 확인한다. 빈 근거·실패 근거로는 성공 처리하지 않는다.
    - 실제 성공 시에만 획득 내용을 로컬 artifact로 저장하고 artifact_ref만 반환한다.
      업무 원문(raw content)은 결과/공유 이벤트에 직접 싣지 않는다(로컬 참조화).
    - P0의 '패키지 미설치 clean' 전제는 파일접근에 그대로 적용하지 않는다.
    - 미지원 procedure.action은 pip 경로로 자동 실행하지 않고 오류로 명확히 거부한다.
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


def _verify_installed(env, target: str, expected_version=None) -> tuple[bool, bool]:
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
    return True, installed_version == (expected_version or harness.TARGET_VERSION)


def _verify_import(env, module=None) -> bool:
    """격리 환경에서 합성 패키지 import 성공 여부를 확인."""
    proc = subprocess.run(
        [env.python_exe, "-c", "import importlib,sys; importlib.import_module(sys.argv[1])", module or harness.TARGET_IMPORT],
        capture_output=True, text=True,
    )
    return proc.returncode == 0


def _apply_pip_install(selected, obs, env, run_id: str, pip_task=None) -> ApplicationResult:
    """P0: 선택 절차를 clean 환경에 적용하고 실제 설치·효과를 검증(동작 불변).

    "실제 성공" = clean 전제 + pip 종료코드 0 + 설치·요구버전 일치 + 합성 import 성공.
    검증의 요구버전·import는 P0 합성 대상(harness.TARGET_VERSION/TARGET_IMPORT) 기준(P1 일반화 지점).
    """
    # 오판 방지: 전역/기존 설치로 인한 거짓 성공 배제.
    # assert가 아닌 명시적 raise — python -O에서도 정직성 전제(가짜 성공 금지)가 유지되어야 함.
    if not harness.is_clean(env, obs.target_pkg):
        raise RuntimeError("clean 환경 전제 위반: 대상 패키지가 이미 설치됨(오판 방지)")

    cfg = selected.procedure
    if pip_task is None:
        index_name = cfg['index']; target = cfg.get('target', obs.target_pkg)
        index_dir = harness.resolve_index(index_name)
        expected_version, module = harness.TARGET_VERSION, harness.TARGET_IMPORT
        install_target = target
    else:
        index_name = cfg['source']; target = pip_task['name']
        if target != obs.target_pkg:
            raise ValueError('Task target differs from observation')
        index_dir = pip_task['source_path']; expected_version = pip_task['version']; module = pip_task['import_module']
        install_target = target + '==' + expected_version
    pip_exit_code = _pip_install(env, index_dir, install_target)
    installed_check, version_check = _verify_installed(env, target, expected_version)
    import_check = _verify_import(env, module)

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
    """B 소유 실행 함수(envharness_p1.run_file_access_procedure)로 위임.

    B 모듈이 아직 이 브랜치/환경에 없으면 미연결 — 호출 시 NotImplementedError.
    (준비/테스트 단계에서는 apply_and_verify(file_access_runner=대역)로 주입한다.
     이 경로로 들어온 '실제 연결' 성공과 대역 테스트 결과는 명확히 구분된다.)
    반환: AccessResult(ok, content, method, evidence).
    """
    try:
        from .envharness_p1 import run_file_access_procedure  # B 소유(1760d32)
    except ImportError as exc:
        raise NotImplementedError(
            "run_file_access_procedure 미연결: envharness_p1(B) 모듈이 아직 없음. "
            "통합 전까지 file_access_runner 대역(AccessResult형)을 주입하세요."
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
    """B의 파일접근 실행 결과(AccessResult)를 재검증하고 로컬 artifact_ref·근거를 반환(S1).

    B 계약: run_file_access_procedure(procedure, env) -> AccessResult(ok, content, method, evidence)
    "실제 성공"(is_real_success)은 ok 플래그만으로 판정하지 않는다. B가 제공한 evidence로
    실제 접근·원본 무변경을 직접 확인한다(가짜/빈/실패 근거 배제):
        - access_ok(True) 이고 content 획득,
        - evidence.original_unchanged is True   (원본 mtime·sha256 무변경),
        - evidence.workbook_readable is True  (접근 최소형태 확인),
        - evidence.save_called is False          (read-only: Save 미호출).
    위를 모두 충족할 때만 획득 내용을 로컬 artifact로 저장하고 참조(artifact_ref)만 반환한다
    (원문 미노출). 하나라도 불충족이면 is_real_success=False, artifact_ref=None.
    """
    runner = file_access_runner or _default_file_access_runner
    outcome = runner(selected.procedure, env)

    access_ok = bool(getattr(outcome, "ok", False))
    method = getattr(outcome, "method", None)
    evidence = getattr(outcome, "evidence", None)
    content = getattr(outcome, "content", None)

    ev = evidence if isinstance(evidence, dict) else {}
    original_unchanged = ev.get("original_unchanged") is True   # 원본 무변경 근거
    completed_rows = ev.get("workbook_readable") is True      # 접근 최소형태
    read_only = ev.get("save_called") is False                  # Save 미호출(read-only)

    access_verified = (
        access_ok
        and content is not None
        and original_unchanged
        and completed_rows
        and read_only
    )
    artifact_ref = _persist_artifact(content, run_id) if access_verified else None
    is_real_success = access_verified and artifact_ref is not None
    return FileAccessResult(
        is_real_success=is_real_success,
        run_id=run_id,
        action=ACTION_FILE_ACCESS,
        access_ok=access_ok,
        access_method=method,
        access_evidence=evidence,
        artifact_ref=artifact_ref,
    )


def apply_and_verify(selected, obs, env, run_id: str, *, file_access_runner=None, pip_task=None):
    """선택된 Skill 절차를 적용하고 실제 효과를 검증. run_id는 전달만(재발급 금지).

    procedure.action 으로 경로 분기(명시적 화이트리스트):
      - "file-access" → 파일접근 검증 경로(FileAccessResult) [P1]
      - "pip-install" → pip 설치·검증 경로(ApplicationResult) [P0, 동작 불변]
      - 그 외/미지정 → 오류(ValueError). 미지원 action을 pip 경로로 자동 실행하지 않는다.
    file_access_runner: B의 run_file_access_procedure 대역 주입점.
      미지정 시 실제 모듈을 late-import(미확정이면 NotImplementedError → 대역과 구분됨).
    """
    from .descriptor import compute_digest
    if compute_digest(vars(selected)) != selected.digest:
        raise ValueError("INTEGRITY_ERROR: current content differs from digest")
    action = selected.procedure.get("action")
    if action == ACTION_FILE_ACCESS:
        return _apply_file_access(selected, obs, env, run_id, file_access_runner)
    if action == ACTION_PIP_INSTALL:
        return _apply_pip_install(selected, obs, env, run_id, pip_task)
    raise ValueError(
        f"지원하지 않는 procedure.action: {action!r} "
        f"(pip 경로 자동 실행 금지 — 지원: {ACTION_PIP_INSTALL!r}, {ACTION_FILE_ACCESS!r})"
    )
