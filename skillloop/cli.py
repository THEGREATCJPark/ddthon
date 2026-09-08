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

# CJ 소유(U3, 읽기전용 파생): 조직 집계·상태줄·대시보드
from . import org_aggregator
from . import statusline as statusline_mod
from . import dashboard as dashboard_mod

# 사전 적재 데모 Skill(합성·비민감). demo_seed=False → 실제 재사용은 실적 반영.
_DEMO_SKILL_CONTENT = {
    "id": "fix-skillloop-demo-pkg-install",
    "version": "1.0.0",
    "origin": {"author": "seed", "note": "preloaded P0 demo skill"},
    "applicability": {"signals": ["pip-install-fail:skillloop-demo-pkg"]},
    "procedure": {"action": "pip-install", "index": "allow", "target": harness.TARGET_PKG},
}

_DEMO_DIR = os.path.join(os.getcwd(), ".skillloop_demo")


def _ensure_utf8_stdout() -> None:
    """Windows-native 콘솔(cp949 등)에서 유니코드 출력 크래시 방지.

    한글·em-dash 등 비-ASCII 출력이 콘솔 코드페이지로 인코딩 실패해 UnicodeEncodeError로
    실행이 중단되는 것을 막는다. 캡처된 스트림(pytest 등)에서는 no-op일 수 있어 예외 무시.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


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
    _ensure_utf8_stdout()
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

        # 6) 실제 성공만 카운트(C3 단독 경로) + 공유 이벤트 생성(C-d).
        #    exact Skill 참조(digest)와 reuser_alias는 호출자(cli)가 제공한다.
        alias = os.environ.get("SKILLLOOP_ALIAS", "local")
        rec = usage.record_actual_reuse(
            build_evidence(
                {"id": selected.id, "version": selected.version, "digest": selected.digest},
                result.__dict__,
                run_id,
                demo_seed=selected.demo_seed,
                reuser_alias=alias,
            )
        )
        print(f"run-p0: reuse={rec.new_count} (counted={rec.counted}, reason={rec.reason})")
        return 0
    finally:
        import shutil
        shutil.rmtree(env.venv_path, ignore_errors=True)


def share_export(out_path: str, usage_path: str | None = None) -> int:
    """C-d: VERIFIED_REUSE 공유 이벤트를 파일로 export(C4/gitsync가 전송할 원본)."""
    usage = UsageTracker(usage_path or os.path.join(_DEMO_DIR, "usage.json"))
    blob = usage.export_shared_usage()
    with open(out_path, "wb") as f:
        f.write(blob)
    n = len(usage.list_shared_events())
    print(f"share-export: {n} event(s) -> {out_path}")
    return 0


def share_import(in_path: str, store_path: str | None = None,
                 usage_path: str | None = None) -> int:
    """C-d: 공유 이벤트 import(재검증·event_id dedup). 로컬 존재 확인=기본 store."""
    store = SkillStore(store_path or os.path.join(_DEMO_DIR, "store.json"))
    usage = UsageTracker(usage_path or os.path.join(_DEMO_DIR, "usage.json"))
    with open(in_path, "rb") as f:
        blob = f.read()

    def _exists(ref: dict) -> bool:
        d = store.get(ref.get("id", ""), ref.get("version", ""))
        return d is not None and d.digest == ref.get("digest")

    results = usage.import_shared_usage(blob, local_ref_exists=_exists)
    applied = sum(1 for r in results if r["applied"])
    print(f"share-import: {applied}/{len(results)} applied (dedup·검증 반영)")
    return 0


def _demo_paths(store_path: str | None, usage_path: str | None) -> tuple[str, str]:
    """P0(run-p0)와 **동일한 기본 경로**를 사용해 로컬 실데이터가 UI에 그대로 보이게 한다."""
    return (
        store_path or os.path.join(_DEMO_DIR, "store.json"),
        usage_path or os.path.join(_DEMO_DIR, "usage.json"),
    )


def _build_local_snapshot(store_path: str | None = None, usage_path: str | None = None) -> dict:
    """로컬 store·usage로 OrgSnapshot 생성(U3 §2.1).

    lifecycle_view·sync_meta는 **미연결(None)** — 계약7(S3 조회)·C4(last_sync)가 B에서
    제공되면 이 자리에 실제 provider를 주입한다. 그 전까지는 '상태 조회 미연결'/'local-only'로
    명시하며, 이미 가능한 로컬 실데이터(Skill·재사용)는 집계·표시한다.
    """
    sp, up = _demo_paths(store_path, usage_path)
    store = SkillStore(sp)
    usage = UsageTracker(up)
    alias = os.environ.get("SKILLLOOP_ALIAS", "local")
    return org_aggregator.build_snapshot(
        store, usage, lifecycle_view=None, sync_meta=None, my_alias=alias,
    )


def cmd_status(store_path: str | None = None, usage_path: str | None = None) -> int:
    """`skillloop status` — 상태줄 한 줄을 stdout으로 출력(로컬 스냅샷 기준).

    이 출력은 그대로 Claude Code 하단 상태줄의 statusLine 커맨드로 연결할 수 있다(README 참조).
    """
    snapshot = _build_local_snapshot(store_path, usage_path)
    print(statusline_mod.render_statusline(snapshot))
    return 0


def cmd_match(signature: str, target: str = "", store_path: str | None = None) -> int:
    """`skillloop match` — 실제 관찰된 실패 신호로 승인된 검색 계약(C5 match.search)을 호출.

    실제 업무 Agent가 관찰한 실패를 그대로 넘겨 재사용 가능한 Skill을 검색한다(FR-MATCH).
    **읽기전용**: 적용·검증·카운트를 하지 않는다 — 매칭 로직은 여기서 재구현하지 않고
    A 소유 `match.search`를 호출만 한다. 실적 카운트는 검증된 경로에서만 발생한다.
    """
    sp, _ = _demo_paths(store_path, None)
    store = SkillStore(sp)
    obs = match_mod.FailureObservation(
        command=(f"pip install {target}" if target else signature),
        target_pkg=target,
        error_signature=signature,
        exit_code=1,
    )
    outcome = match_mod.search(obs, store)
    if outcome.status == match_mod.STATUS_MATCH:
        d = outcome.descriptor
        proc = getattr(d, "procedure", {}) or {}
        print(f"match: MATCH {d.id}@{d.version} digest={d.digest[:12]}")
        print(f"match: 적용 절차(참고) action={proc.get('action')} "
              f"index={proc.get('index')} target={proc.get('target', target)}")
        print(f"match: {outcome.rationale}")
        print("match: 이 절차를 실제 업무에 적용·검증한 뒤에만 실적으로 보고하세요"
              "(카운트는 검증 성공 경로에서만; 원격 Skill은 명시적 확인 후 실행).")
        return 0
    print(f"match: {outcome.status} — {outcome.rationale}")
    return 0


def cmd_dashboard(host: str = "127.0.0.1", port: int = 8765,
                  store_path: str | None = None, usage_path: str | None = None) -> int:
    """`skillloop dashboard` — 127.0.0.1 읽기전용 대시보드 기동(요청마다 스냅샷 재생성)."""
    def provider() -> dict:
        return _build_local_snapshot(store_path, usage_path)
    dashboard_mod.serve_readonly(provider, host=host, port=port)
    return 0


def main(argv: list[str] | None = None) -> int:
    """콘솔 스크립트 진입점. 서브커맨드 라우팅."""
    _ensure_utf8_stdout()
    parser = argparse.ArgumentParser(prog="skillloop")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run-p0", help="P0 재사용 데모 실행")
    pe = sub.add_parser("share-export", help="VERIFIED_REUSE 공유 이벤트 export")
    pe.add_argument("out", help="export 파일 경로")
    pi = sub.add_parser("share-import", help="공유 이벤트 import(검증·dedup)")
    pi.add_argument("inp", help="import 파일 경로")
    sub.add_parser("status", help="상태줄 한 줄 출력(조직 현황, 읽기전용)")
    pm = sub.add_parser("match", help="관찰된 실패 신호로 재사용 Skill 검색(읽기전용, 적용·카운트 없음)")
    pm.add_argument("--signature", required=True, help="관찰된 실패 신호(예: pip-install-fail:pkg)")
    pm.add_argument("--target", default="", help="대상 패키지(선택, 표시용)")
    pd = sub.add_parser("dashboard", help="localhost 읽기전용 대시보드 기동")
    pd.add_argument("--host", default="127.0.0.1", help="바인딩 호스트(기본 127.0.0.1)")
    pd.add_argument("--port", type=int, default=8765, help="포트(기본 8765)")
    args = parser.parse_args(argv)
    if args.command == "run-p0":
        return run_p0()
    if args.command == "share-export":
        return share_export(args.out)
    if args.command == "share-import":
        return share_import(args.inp)
    if args.command == "status":
        return cmd_status()
    if args.command == "match":
        return cmd_match(args.signature, args.target)
    if args.command == "dashboard":
        return cmd_dashboard(host=args.host, port=args.port)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
