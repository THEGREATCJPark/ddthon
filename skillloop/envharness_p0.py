"""C7 P0 — 오프라인 결정적 실행 환경(이중 mock index + 격리 venv).

소유(단일 수정자): CJ
계약(Code Plan §1, §2):
    - prepare() -> None                 failing/allow 두 index 준비(정답 강제 아님)
    - setup_failing() -> EnvCtx         대상 패키지 없는 index
    - setup_allow() -> EnvCtx           합성 패키지 있는 index(적용은 descriptor.procedure가 결정)
    - make_clean_venv() -> EnvCtx       격리 venv 생성
    - is_clean(env, target_pkg) -> bool 대상 패키지 미설치 확인(오판 방지)
    - resolve_index(name) -> str        index 이름("failing"/"allow") → 로컬 디렉터리(호출 계약)

"네트워크 미의존" = 외부 인터넷 미의존. pip은 `--no-index --find-links <dir>`로 로컬만.
harness는 두 index를 제공만 하며, 실제 적용 index는 선택된 descriptor.procedure에서 취득.
"""

from __future__ import annotations

import glob
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass

# 데모 대상 배포 패키지(pip 이름)와 import 이름.
TARGET_PKG = "skillloop-demo-pkg"
TARGET_IMPORT = "skillloop_demo_pkg"
TARGET_VERSION = "1.0.0"

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)
_FIXTURES = os.path.join(_REPO_ROOT, "tests", "fixtures")
_SYNTHETIC_SRC = os.path.join(_FIXTURES, "synthetic_pkg")
_INDEXES = os.path.join(_FIXTURES, "indexes")


@dataclass
class EnvCtx:
    venv_path: str = ""          # 격리 venv 경로
    index_url: str = ""          # 로컬 index 디렉터리(find-links 대상)
    python_exe: str = ""         # venv 내 python 실행 파일
    kind: str = ""               # "failing" | "allow" | "clean"


def resolve_index(name: str) -> str:
    """index 이름을 로컬 디렉터리 경로로 해석. reuse_service(A)가 절차 기반으로 호출."""
    if name not in ("failing", "allow"):
        raise ValueError(f"unknown index: {name!r}")
    return os.path.join(_INDEXES, name)


def _venv_python(venv_path: str) -> str:
    if os.name == "nt":
        return os.path.join(venv_path, "Scripts", "python.exe")
    return os.path.join(venv_path, "bin", "python")


def _allow_has_target() -> bool:
    return bool(glob.glob(os.path.join(resolve_index("allow"), "skillloop_demo_pkg-*.whl")))


def prepare() -> None:
    """failing/allow 두 로컬 index 준비. allow에 합성 패키지 wheel을 오프라인 빌드.

    어느 index가 정답인지 강제하지 않는다(정합화 3). 실제 적용 index는 descriptor.procedure가 결정.
    """
    os.makedirs(resolve_index("failing"), exist_ok=True)  # 비어 있음(대상 패키지 없음)
    allow = resolve_index("allow")
    os.makedirs(allow, exist_ok=True)
    if not _allow_has_target():
        # 오프라인 wheel 빌드(--no-index --no-build-isolation): 외부 인터넷 미의존.
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", _SYNTHETIC_SRC,
             "--no-index", "--no-build-isolation", "-w", allow],
            check=True, capture_output=True, text=True,
        )


def setup_failing() -> EnvCtx:
    """대상 패키지가 없는 실패 index 컨텍스트."""
    return EnvCtx(index_url=resolve_index("failing"), kind="failing")


def setup_allow() -> EnvCtx:
    """합성 패키지가 있는 허용 index 컨텍스트."""
    return EnvCtx(index_url=resolve_index("allow"), kind="allow")


def make_clean_venv() -> EnvCtx:
    """실행마다 격리된 clean venv 생성(pip 포함)."""
    venv_path = tempfile.mkdtemp(prefix="skillloop_venv_")
    subprocess.run(
        [sys.executable, "-m", "venv", venv_path],
        check=True, capture_output=True, text=True,
    )
    return EnvCtx(venv_path=venv_path, python_exe=_venv_python(venv_path), kind="clean")


def is_clean(env: EnvCtx, target_pkg: str) -> bool:
    """env에 target_pkg가 설치되어 있지 않은지 확인(전역 설치로 인한 오판 배제)."""
    py = env.python_exe or sys.executable
    proc = subprocess.run(
        [py, "-m", "pip", "show", target_pkg],
        capture_output=True, text=True,
    )
    # pip show는 미설치 시 비영점 종료코드 → clean.
    return proc.returncode != 0
