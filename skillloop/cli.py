"""C8 — CLI 진입점: `skillloop run-p0` 오케스트레이션.

소유(단일 수정자): CJ
계약(Code Plan §1, §3):
    - run_p0() -> int

흐름(R5):
    run_id = usage.new_execution_id()            # 발급 지점(실행 시작 1회)
    prepare → make_clean_venv → setup_failing → 실제 pip 실패 관찰 → match.search
      → MATCH: reuse_service.apply_and_verify(selected, obs, env, run_id)
          → 성공: usage.record_actual_reuse(build_evidence(..., run_id, ...)) → "reuse=N"
      → NO_MATCH/ERROR/TIMEOUT/검증실패: 상태 출력(카운트 없음)
run_id는 cli가 1회 발급해 S1→검증→C3까지 전달만. 재시도 시 기존 run_id 재사용.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from . import envharness_p0 as harness
from . import descriptor as descriptor_mod
from .store import SkillStore
from .usage import UsageTracker, build_evidence, new_execution_id

# A 소유(호출만): 결정적 검색 + 시나리오 비의존 적용·검증
from . import match as match_mod
from . import reuse_service

# 사전 적재 데모 Skill(합성·비민감). demo_seed=False → 실제 재사용은 실적 반영.
_DEMO_SKILL_CONTENT = {
    "id": "fix-skillloop-demo-pkg-install",
    "version": "1.0.0",
    "origin": {"author": "seed", "note": "preloaded P0 demo skill"},
    "applicability": {"signals": ["pip-install-fail:skillloop-demo-pkg"]},
    "procedure": {"action": "pip-install", "index": "allow", "target": harness.TARGET_PKG},
}

_DEMO_DIR = os.path.join(os.getcwd(), ".skillloop_demo")


def _seed_store(store: SkillStore) -> None:
    d = descriptor_mod.make_descriptor(_DEMO_SKILL_CONTENT, demo_seed=False)
    store.put(d)  # STORED 또는 DEDUP(재실행 시). 카운트 변경 없음.


def _observe_failing_install(env, index_dir: str, target: str):
    """failing index로 실제 pip 설치를 시도해 실패를 관찰(비영점 종료코드)."""
    proc = subprocess.run(
        [env.python_exe, "-m", "pip", "install",
         "--no-index", "--find-links", index_dir, target],
        capture_output=True, text=True,
    )
    signature = f"pip-install-fail:{target}"
    return match_mod.FailureObservation(
        command=f"pip install {target}",
        target_pkg=target,
        error_signature=signature,
        exit_code=proc.returncode,
    )


def run_p0(store_path: str | None = None, usage_path: str | None = None,
           run_id: str | None = None) -> int:
    """P0 데모: 설치 실패 → Skill 적용 → 실제 검증 → reuse+1. 종료코드 반환.

    run_id=None이면 새 논리적 실행으로 1회 발급(발급 지점).
    동일 실행의 재시도·재시작이면 호출자가 기존 run_id를 전달 → 중복 카운트 방지(C3 dedup).
    """
    os.makedirs(_DEMO_DIR, exist_ok=True)
    store = SkillStore(store_path or os.path.join(_DEMO_DIR, "store.json"))
    usage = UsageTracker(usage_path or os.path.join(_DEMO_DIR, "usage.json"))
    _seed_store(store)

    # 1) 실행 식별자: 새 실행이면 1회 발급, 재시도·재시작이면 전달받은 것 재사용.
    if run_id is None:
        run_id = new_execution_id()

    # 2) 오프라인 index 준비 + clean venv.
    harness.prepare()
    env = harness.make_clean_venv()
    try:
        # 3) failing index로 실제 실패 관찰.
        failing = harness.setup_failing()
        obs = _observe_failing_install(env, failing.index_url, harness.TARGET_PKG)
        if obs.exit_code == 0:
            print("run-p0: FAIL 재현 실패(failing index에 대상 존재?) — 중단")
            return 3
        print(f"run-p0: pip install 실패 관찰(exit={obs.exit_code})")

        # 4) 결정적 검색(A/C5).
        outcome = match_mod.search(obs, store)
        if outcome.status != "MATCH":
            print(f"run-p0: {outcome.status} — 카운트 없음. {outcome.rationale}")
            return 0
        selected = outcome.descriptor
        print(f"run-p0: MATCH {selected.id}@{selected.version} — {outcome.rationale}")

        # 5) 적용+검증(A/S1). run_id 전달만(재발급 금지).
        result = reuse_service.apply_and_verify(selected, obs, env, run_id)
        if not result.is_real_success:
            print(f"run-p0: 적용했으나 검증 실패(exit={result.pip_exit_code}) — 카운트 없음")
            return 0

        # 6) 실제 성공만 카운트(C3 단독 경로).
        rec = usage.record_actual_reuse(
            build_evidence(
                {"id": selected.id, "version": selected.version},
                result.__dict__,
                run_id,
                demo_seed=selected.demo_seed,
            )
        )
        print(f"run-p0: reuse={rec.new_count} (counted={rec.counted}, reason={rec.reason})")
        return 0
    finally:
        import shutil
        shutil.rmtree(env.venv_path, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    """콘솔 스크립트 진입점. 서브커맨드 라우팅."""
    parser = argparse.ArgumentParser(prog="skillloop")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run-p0", help="P0 재사용 데모 실행")
    args = parser.parse_args(argv)
    if args.command == "run-p0":
        return run_p0()
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
