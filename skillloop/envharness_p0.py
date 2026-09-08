"""C7 P0 — 오프라인 결정적 실행 환경(이중 mock index + 격리 venv).

소유(단일 수정자): CJ
계약(Code Plan §1, §2):
    - prepare() -> None                 failing/allow 두 index 준비(정답 강제 아님)
    - setup_failing() -> EnvCtx         대상 패키지 없는 index
    - setup_allow() -> EnvCtx           합성 패키지 있는 index(적용은 descriptor.procedure가 결정)
    - make_clean_venv() -> EnvCtx       격리 venv 생성
    - is_clean(env, target_pkg) -> bool 대상 패키지 미설치 확인(오판 방지)

"네트워크 미의존" = 외부 인터넷 미의존. pip은 `--no-index --find-links <dir>`로 로컬만.
harness는 두 index를 제공만 하며, 실제 적용 index는 선택된 descriptor.procedure에서 취득.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EnvCtx:
    venv_path: str = ""          # 격리 venv 경로
    index_url: str = ""          # 로컬 index 디렉터리(find-links 대상)
    python_exe: str = ""         # venv 내 python 실행 파일
    kind: str = ""               # "failing" | "allow" | "clean"


def prepare() -> None:
    """failing/allow 두 로컬 index를 준비. 어느 index가 정답인지 강제하지 않음."""
    raise NotImplementedError("S5")


def setup_failing() -> EnvCtx:
    """대상 패키지가 없는 실패 index 컨텍스트."""
    raise NotImplementedError("S5")


def setup_allow() -> EnvCtx:
    """합성 패키지가 있는 허용 index 컨텍스트."""
    raise NotImplementedError("S5")


def make_clean_venv() -> EnvCtx:
    """실행마다 격리된 clean venv 생성."""
    raise NotImplementedError("S5")


def is_clean(env: EnvCtx, target_pkg: str) -> bool:
    """env에 target_pkg가 설치되어 있지 않은지 확인(전역 설치로 인한 오판 배제)."""
    raise NotImplementedError("S5")
