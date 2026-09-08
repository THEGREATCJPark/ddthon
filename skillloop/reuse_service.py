"""S1 — ReuseService: 시나리오 비의존 적용 + 실제 효과 검증 + 실제 성공 판정.

소유(단일 수정자): A (최호길) — 이 파일은 A만 편집. 인계 후 CJ 동시 수정 금지.
계약(Code Plan §1, §3):
    - apply_and_verify(selected, obs, env, run_id) -> ApplicationResult

규칙(RU2, 정정 Q3·정합화 2·3):
    - run_id는 호출자(cli)가 발급해 전달 — S1 내부 재발급 금지(재시도 시 동일 run_id 수신).
    - assert is_clean(env, obs.target_pkg)로 오판 방지.
    - cfg = selected.procedure — 적용 index/옵션은 절차에서 취득(정답 환경 강제 아님).
    - execute pip install(cfg) → 검증: exit0 & 설치 & 요구버전 & (합성)import.
    - "실제 성공" = 위 검증 통과. 성공 index 선택 자체는 성공 근거 아님.
CJ 소유 계약(envharness_p0)은 호출만.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from . import envharness_p0 as harness


@dataclass
class ApplicationResult:
    pip_exit_code: int
    installed_check: bool
    version_check: bool
    import_check: bool
    index_source: str
    is_real_success: bool
    run_id: str


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


def apply_and_verify(selected, obs, env, run_id: str) -> ApplicationResult:
    """선택된 Skill 절차를 clean 환경에 적용하고 실제 설치·효과를 검증. run_id는 전달만.

    "실제 성공"(is_real_success)은 다음을 모두 충족할 때만(RU2):
      1) clean 환경 전제(대상 패키지 미설치), 2) pip 종료코드 0,
      3) 대상 패키지 설치 + 요구 버전 일치, 4) 합성 패키지 import 성공.
    성공 index를 '선택'했다는 사실 자체는 성공 근거가 아니며, 실제 실행 결과로만 판정한다.
    적용 설정(index/target)은 selected.procedure에서 취득한다(harness 정답 강제 아님).
    검증의 요구버전·import 확인은 P0 합성 대상(harness.TARGET_VERSION/TARGET_IMPORT) 기준이며,
    대상별(descriptor 선언 버전/모듈) 일반화는 P1 확장 지점이다(RU4).
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
