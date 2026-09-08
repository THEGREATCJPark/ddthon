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

from dataclasses import dataclass


@dataclass
class ApplicationResult:
    pip_exit_code: int
    installed_check: bool
    version_check: bool
    import_check: bool
    index_source: str
    is_real_success: bool
    run_id: str


def apply_and_verify(selected, obs, env, run_id: str) -> ApplicationResult:
    """선택된 Skill 절차를 clean 환경에 적용하고 실제 설치·효과를 검증. run_id는 전달만."""
    raise NotImplementedError("S8")
