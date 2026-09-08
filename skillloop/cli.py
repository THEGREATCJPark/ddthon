"""C8 — CLI 진입점: `skillloop run-p0` 오케스트레이션.

소유(단일 수정자): CJ
계약(Code Plan §1, §3):
    - run_p0() -> int

흐름(R5):
    run_id = usage.new_execution_id()            # 발급 지점(실행 시작 1회)
    prepare → setup_failing → 실제 pip 실패 관찰 → match.search
      → MATCH: reuse_service.apply_and_verify(selected, obs, env, run_id)
          → 성공: usage.record_actual_reuse(build_evidence(..., run_id, ...)) → "reuse=N"
      → NO_MATCH/ERROR/TIMEOUT/검증실패: 상태 출력(카운트 없음)
run_id는 cli가 1회 발급해 S1→검증→C3까지 전달만. 재시도 시 기존 run_id 재사용.
"""

from __future__ import annotations

import argparse
import sys


def run_p0() -> int:
    """P0 데모: 설치 실패 → Skill 적용 → 실제 검증 → reuse+1. 종료코드 반환."""
    raise NotImplementedError("S9")


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
