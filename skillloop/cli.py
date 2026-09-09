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
import getpass
import json
import os
import re
from pathlib import Path
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


def _package_name(requirement: str) -> str:
    """Normalize an observed distribution name, never a Skill identity."""
    parsed = re.fullmatch(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)(?:==[^\s;]+)?\s*", requirement)
    if not parsed:
        raise ValueError("INVALID_TARGET: use a distribution name or name==version")
    return re.sub(r"[-_.]+", "-", parsed.group(1)).lower()


def _pip_failure_observation(command: str, target: str, exit_code: int, stderr: str):
    """Actual pip supply failure -> stable FailureObservation; no Skill/solution lookup."""
    name = _package_name(target)
    if type(exit_code) is not int or exit_code == 0:
        return None
    pattern = (r"(?:no matching distribution found for|could not find a version that "
               r"satisfies the requirement)\s+([^\s(]+)")
    for found in re.finditer(pattern, stderr, re.IGNORECASE):
        try:
            failed_name = _package_name(found.group(1))
        except ValueError:
            continue
        if failed_name == name:
            return match_mod.FailureObservation(
                command=command, target_pkg=name, error_signature=f"pip-install-fail:{name}",
                exit_code=exit_code)
    return None


def _observe_failing_install(env, index_dir: str, target: str):
    """failing index로 실제 pip 설치를 시도해 실패를 관찰(비영점 종료코드)."""
    proc = subprocess.run(
        [env.python_exe, "-m", "pip", "install",
         "--no-index", "--find-links", index_dir, target],
        capture_output=True, text=True,
    )
    obs = _pip_failure_observation(f"pip install {target}", target, proc.returncode, proc.stderr)
    return obs or match_mod.FailureObservation(
        command=f"pip install {target}", target_pkg=target,
        error_signature="", exit_code=proc.returncode)


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


def _parse_work_requirements(text: str) -> str:
    """지원 밖의 입력을 무시하거나 다른 대상으로 바꾸지 않는다."""
    lines = [line.split("#", 1)[0].strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    expected = f"{harness.TARGET_PKG}=={harness.TARGET_VERSION}"
    if lines != [expected]:
        raise ValueError("UNSUPPORTED_REQUIREMENTS: supported request is " + expected)
    return harness.TARGET_PKG


def apply_requirements(requirements: str, python: str, store_path: str,
                       usage_path: str, run_id: str | None = None, policy_path: str | None = None) -> int:
    """기존 작업 환경에 실제 설치. 환경 준비·seed·삭제는 하지 않는다."""
    _ensure_utf8_stdout()
    run_id = run_id or new_execution_id()
    print(f"apply-requirements: run_id={run_id}")
    try:
        req = Path(requirements).resolve(strict=True)
        text = req.read_text(encoding='utf-8-sig')
        policy = json.loads(Path(policy_path).read_text(encoding='utf-8')) if policy_path else None
        task = None
        if policy is None:
            target = _parse_work_requirements(text)
        else:
            lines = [line.split('#', 1)[0].strip() for line in text.splitlines()]
            lines = [line for line in lines if line]
            parsed = re.fullmatch(r'([A-Za-z0-9][A-Za-z0-9._-]*)==([A-Za-z0-9][A-Za-z0-9.!+_-]*)', lines[0]) if len(lines) == 1 else None
            if not parsed:
                raise ValueError('UNSUPPORTED_REQUIREMENTS: one pinned local distribution required')
            target, version = _package_name(parsed.group(1)), parsed.group(2)
            module = policy.get('imports', {}).get(target)
            if not isinstance(module, str) or not re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*', module):
                raise ValueError('POLICY_REQUIRED: approved import mapping missing')
            task = {'name': target, 'version': version, 'import_module': module}
        py = Path(python).absolute()
        if not py.is_file():
            raise ValueError("ENV_NOT_READY: target Python missing")
        probe = subprocess.run(
            [str(py), "-c", "import json,sys; print(json.dumps([sys.prefix,sys.base_prefix]))"],
            capture_output=True, text=True, timeout=30)
        if probe.returncode:
            raise ValueError("ENV_NOT_READY: target Python unavailable")
        prefix, base = json.loads(probe.stdout)
        if prefix == base:
            raise ValueError("ENV_NOT_READY: an existing work venv is required")
        pip_probe = subprocess.run([str(py), "-m", "pip", "--version"],
                                   capture_output=True, text=True, timeout=30)
        if pip_probe.returncode:
            raise ValueError("ENV_NOT_READY: target pip unavailable")
        sp, up = Path(store_path).absolute(), Path(usage_path).absolute()
        if not sp.is_file():
            raise ValueError("STORE_NOT_READY: existing store required")
        if up == sp or up == req or up == py:
            raise ValueError("INVALID_USAGE_PATH: must not overwrite work inputs")
        store = SkillStore(str(sp))
        usage = UsageTracker(str(up))
        env = harness.EnvCtx(venv_path=prefix, python_exe=str(py), kind="work")
        print(f"apply-requirements: requirements={req} python={py}")
        command = [str(py), "-m", "pip", "install", "-r", str(req)]
        observed = subprocess.run(command, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=120)
        print(f"apply-requirements: install exit={observed.returncode}")
        print(observed.stdout.strip())
        print(observed.stderr.strip())
        if observed.returncode == 0:
            print("apply-requirements: INSTALL_OK_NO_REUSE reuse_delta=0; no Skill applied")
            return 0
        obs = _pip_failure_observation(
            subprocess.list2cmdline(command), target, observed.returncode, observed.stderr)
        if obs is None:
            print("apply-requirements: INSTALL_ERROR (not a package-supply signal), reuse_delta=0")
            return 4
        print(f"apply-requirements: observation={obs.error_signature} target={obs.target_pkg}")
        print("현재 설정으로 패키지를 설치하지 못했습니다. Skill 저장소에서 해결 방법을 찾아보겠습니다.")
        outcome = match_mod.search(obs, store)
        print(f"apply-requirements: {outcome.status} {outcome.rationale}")
        if outcome.status != "MATCH":
            return 5
        selected = outcome.descriptor
        print(f"apply-requirements: selected={selected.id}@{selected.version} digest={selected.digest}")
        print("apply-requirements: procedure=" + json.dumps(selected.procedure, ensure_ascii=False))
        if descriptor_mod.compute_digest(vars(selected)) != selected.digest:
            raise ValueError("INTEGRITY_ERROR: selected content digest mismatch")
        cfg = selected.procedure
        if policy is None:
            if cfg.get('action') != 'pip-install' or cfg.get('target') != target:
                raise ValueError('UNSUPPORTED_PROCEDURE: action/target does not match request')
            if selected.digest != descriptor_mod.compute_digest(_DEMO_SKILL_CONTENT):
                raise ValueError('CONFIRMATION_REQUIRED: Skill is outside the preapproved P0 content')
        else:
            ref = {key: getattr(selected, key) for key in ('id', 'version', 'digest')}
            if ref not in policy.get('approved_skills', []):
                raise ValueError('CONFIRMATION_REQUIRED: exact content not approved in local policy')
            if set(cfg) != {'action', 'source'} or cfg['action'] != 'pip-install':
                raise ValueError('UNSUPPORTED_PROCEDURE: environment-only package source required')
            source = policy.get('sources', {}).get(cfg['source'])
            if not isinstance(source, str) or not Path(source).is_dir():
                raise ValueError('POLICY_REQUIRED: approved local source missing')
            task['source_path'] = str(Path(source).resolve())
        result = (reuse_service.apply_and_verify(selected, obs, env, run_id, pip_task=task) if task is not None
                  else reuse_service.apply_and_verify(selected, obs, env, run_id))
        print("apply-requirements: verification=" + json.dumps(vars(result), ensure_ascii=False))
        if not result.is_real_success:
            print("apply-requirements: VERIFICATION_FAILED reuse_delta=0")
            return 6
        rec = usage.record_actual_reuse(build_evidence(
            {"id": selected.id, "version": selected.version, "digest": selected.digest},
            vars(result), run_id, demo_seed=selected.demo_seed,
            reuser_alias=os.environ.get("SKILLLOOP_ALIAS", "local")))
        print(f"apply-requirements: reuse={rec.new_count} counted={rec.counted} reason={rec.reason}")
        title = statusline_mod.skill_title(selected.id, selected.version)
        if rec.counted:
            print(f"‘{title}’ Skill로 설치와 사용 확인을 마쳤습니다. "
                  f"검증된 재사용 성공 기록이 1회 추가됐습니다(로컬 누적 {rec.new_count}회).")
        else:
            print(f"‘{title}’ Skill의 적용 결과를 확인했습니다. 이번 처리로 재사용 기록은 추가되지 않았습니다.")
        print("apply-requirements: WORK_ENV_PRESERVED candidate_delta=0")
        return 0
    except subprocess.TimeoutExpired:
        print("apply-requirements: TIMEOUT; no reuse recorded; work environment preserved")
        return 7
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print(f"apply-requirements: ERROR {exc}; no reuse recorded; work environment preserved")
        return 2


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
    lifecycle, sync = _lifecycle_providers(store)
    return org_aggregator.build_snapshot(
        store, usage, lifecycle_view=lifecycle, sync_meta=sync, my_alias=alias,
    )


def _lifecycle_providers(store):
    from .publish_pipeline import PublishPipeline
    from .gitsync import GitSyncAdapter
    # A missing lifecycle source remains visibly unlinked for existing P0 workspaces.
    lifecycle = PublishPipeline(store) if store.list_lifecycle_records() else None
    config = Path(store.path).parent / 'sync-config.local.json'
    data = json.loads(config.read_text(encoding='utf-8')) if config.is_file() else None
    sync = GitSyncAdapter(data['mirror'], data['remote']) if data else None
    return lifecycle, sync


def cmd_status(store_path: str | None = None, usage_path: str | None = None,
               team: str = "디디톤 기술혁신팀", alias: str | None = None) -> int:
    """`skillloop status` — 상태줄 네 줄을 stdout으로 출력(명시 작업 경로/로컬 스냅샷 기준).

    이 출력은 그대로 Claude Code 하단 상태줄의 statusLine 커맨드로 연결할 수 있다(README 참조).
    """
    try:
        context_path = Path.cwd() / "skillloop-work.json"
        context = json.loads(context_path.read_text(encoding="utf-8")) if context_path.is_file() else {}
        def resolve_context_path(name):
            value = context.get(name)
            return str((context_path.parent / value).resolve()) if value else None
        sp, up = _demo_paths(store_path or resolve_context_path("store"),
                             usage_path or resolve_context_path("usage"))
        store = SkillStore(sp)
        lifecycle, sync = _lifecycle_providers(store)
        snapshot = org_aggregator.build_snapshot(
            store, UsageTracker(up), lifecycle_view=lifecycle, sync_meta=sync,
            my_alias=alias or os.environ.get("SKILLLOOP_ALIAS") or getpass.getuser())
        print(statusline_mod.render_statusline(snapshot, team=team))
        return 0
    except (OSError, ValueError, KeyError, TypeError):
        print("🧠 SkillLoop · 상태 데이터 읽기 실패\n📚 Skill 현황 확인 불가"
              "\n✨ 기여·인기 집계 확인 불가\n데모/실제 검증 확인 불가")
        return 2


def cmd_match(signature: str | None, target: str = "", store_path: str | None = None,
              pip_stderr: str | None = None, exit_code: int | None = None) -> int:
    """`skillloop match` — 실제 관찰된 실패 신호로 승인된 검색 계약(C5 match.search)을 호출.

    실제 업무 Agent가 관찰한 실패를 그대로 넘겨 재사용 가능한 Skill을 검색한다(FR-MATCH).
    **읽기전용**: 적용·검증·카운트를 하지 않는다 — 매칭 로직은 여기서 재구현하지 않고
    A 소유 `match.search`를 호출만 한다. 실적 카운트는 검증된 경로에서만 발생한다.
    """
    if pip_stderr is not None and not store_path:
        print("match: STORE_REQUIRED — specify the observed work's --store; search not invoked")
        return 2
    sp, _ = _demo_paths(store_path, None)
    store = SkillStore(sp)
    if pip_stderr is not None:
        if not target or exit_code is None:
            print("match: INVALID_OBSERVATION — target and actual exit-code required; search not invoked")
            return 2
        try:
            obs = _pip_failure_observation(
                f"pip install {target}", target, exit_code,
                Path(pip_stderr).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            print(f"match: INVALID_OBSERVATION — {exc}; search not invoked")
            return 2
        if obs is None:
            print("match: NOT_INVOKED — not a recognized failed supply observation")
            return 4
        print(f"match: observation={obs.error_signature} target={obs.target_pkg}")
    else:
        if signature and re.search(r"no matching distribution|could not find a version", signature, re.I):
            print("match: INVALID_SIGNAL — raw pip error requires --pip-stderr, --exit-code, --target; search not invoked")
            return 2
        obs = match_mod.FailureObservation(
            command=(f"pip install {target}" if target else signature),
            target_pkg=target, error_signature=signature or "", exit_code=1)
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


def cmd_p1(args):
    """Explicit CLI boundaries: discovery belongs to Agent; review belongs to person."""
    from .experience_service import run_p1
    from .publish_pipeline import PublishPipeline
    from .envharness_p1 import EnvContext
    from .gitsync import GitSyncAdapter
    try:
        if args.command == 'run-p1':
            procedure = json.loads(Path(args.procedure).read_text(encoding='utf-8')) if args.procedure else None
            return run_p1(args.xlsx, args.store, args.usage, args.run_id, app_open=args.app_open,
                          procedure=procedure, confirmed_digest=args.confirm_skill, author=args.author,
                          task_mapping=json.loads(Path(args.task_mapping).read_text(encoding='utf-8')) if args.task_mapping else None)
        store = SkillStore(args.store)
        pipeline = PublishPipeline(store)
        if args.command in ('store-init', 'sync'):
            adapter = GitSyncAdapter(args.mirror, args.remote)
            if args.command == 'store-init':
                adapter.initialize()
                config = Path(args.store).parent / 'sync-config.local.json'
                config.parent.mkdir(parents=True, exist_ok=True)
                config.write_text(json.dumps({'mirror': str(adapter.path), 'remote': args.remote}), encoding='utf-8')
                print('store-init: isolated mirror prepared; no publication claimed')
                return 0
            usage = UsageTracker(args.usage)
            result = adapter.pull(store, usage)
            if result.get('ok') and args.push_usage:
                result['usage_push'] = adapter.push_shared_usage(usage.export_shared_usage())
            print(json.dumps(result, ensure_ascii=False))
            return 0 if result.get('ok') and result.get('usage_push', {}).get('ok', True) else 2
        candidate = store.get(args.id, args.version)
        if candidate is None:
            raise ValueError('Candidate not found')
        if args.command == 'review':
            print(json.dumps({'id': candidate.id, 'version': candidate.version, 'digest': candidate.digest,
                              'procedure': candidate.procedure}, ensure_ascii=False, indent=2))
            typed = input(f'Human review: type "{args.decision} {candidate.digest}" to confirm: ').strip()
            if typed != f'{args.decision} {candidate.digest}':
                print('Review not recorded')
                return 2
            result = pipeline.review(candidate, args.decision, args.reviewer)
        elif args.command == 'replay':
            result = pipeline.replay(candidate, EnvContext(args.xlsx, args.app_open))
        else:
            result = pipeline.publish(candidate, GitSyncAdapter(args.mirror, args.remote))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['state'] not in ('BLOCKED', 'PUBLISH_PENDING', 'REJECTED') else 2
    except (OSError, ValueError, RuntimeError, EOFError) as exc:
        print(f'{args.command}: ERROR {exc}')
        return 2


def main(argv: list[str] | None = None) -> int:
    """콘솔 스크립트 진입점. 서브커맨드 라우팅."""
    _ensure_utf8_stdout()
    parser = argparse.ArgumentParser(prog="skillloop")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run-p0", help="P0 재사용 데모 실행")
    pa = sub.add_parser("apply-requirements", help="기존 작업 venv의 합성 requirements 설치·Skill 재사용")
    pa.add_argument("--requirements", required=True)
    pa.add_argument("--python", required=True, help="기존 작업 venv Python")
    pa.add_argument("--store", required=True, help="준비된 로컬 Skill store")
    pa.add_argument("--usage", required=True)
    pa.add_argument("--run-id")
    pa.add_argument("--policy", help="운영자가 준비한 exact 승인·공급원·import 매핑 JSON")
    pe = sub.add_parser("share-export", help="VERIFIED_REUSE 공유 이벤트 export")
    pe.add_argument("out", help="export 파일 경로")
    pi = sub.add_parser("share-import", help="공유 이벤트 import(검증·dedup)")
    pi.add_argument("inp", help="import 파일 경로")
    ps = sub.add_parser("status", help="Claude 하단 상태줄 네 줄(읽기전용)")
    ps.add_argument("--store")
    ps.add_argument("--usage")
    ps.add_argument("--team", default="디디톤 기술혁신팀")
    ps.add_argument("--alias")
    pm = sub.add_parser("match", help="관찰된 실패 신호로 재사용 Skill 검색(읽기전용, 적용·카운트 없음)")
    mg = pm.add_mutually_exclusive_group(required=True)
    mg.add_argument("--signature", help="기존 정규화된 applicability 신호")
    mg.add_argument("--pip-stderr", help="실제 pip stderr UTF-8 파일")
    pm.add_argument("--exit-code", type=int, help="실제 pip 종료코드")
    pm.add_argument("--target", default="", help="대상 패키지(선택, 표시용)")
    pm.add_argument("--store", help="실제 업무의 Skill store 경로")
    pd = sub.add_parser("dashboard", help="localhost 읽기전용 대시보드 기동")
    pd.add_argument("--host", default="127.0.0.1", help="바인딩 호스트(기본 127.0.0.1)")
    pd.add_argument("--port", type=int, default=8765, help="포트(기본 8765)")
    p1 = sub.add_parser('run-p1', help='실제 XLSX 실패·검색·Agent 절차 적용·업무·후보화',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''입력 계약 (현재 문서의 정답 배치를 제공하는 것이 아닙니다):
  --task-mapping: JSON object, 정확히 sheet/month_col/total_col/first_row 네 key.
    sheet: 실제 snapshot에서 확인한 시트 이름(string).
    month_col, total_col, first_row: 1-based positive integer.
    UsedRange 상대 좌표가 아닌 worksheet 절대 좌표. month_col != total_col.
  --procedure: 실제 발견한 접근이 지원 어댑터와 일치하는 경우에만
    {"action":"file-access","method":"excel-com-attach"}를 전달.
    업무 데이터/시트/열/행/예측식/암호/파일 경로는 procedure에 포함하지 않음.
  NEEDS_AGENT_DISCOVERY: 실제 실패·검색 후 정상적인 환경 사실 확인 대기.
    사용자에게 Excel 열람 가능 여부를 확인하고 답변 뒤 탐색합니다.
  NEEDS_TASK_MAPPING: 로컬 artifact_ref를 읽어 현재 문서의 실제 배치를 판단.
  --app-open은 보고된 전제이며 실제 workbook 접근 성공의 증명이 아닙니다.
  WORK_COMPLETE의 chart_ref는 최종 답변에 실제 파일 경로/링크로 전달합니다.
  검색 범위는 Team Skill. 별도 Org Knowledge 입력은 현재 제공되지 않습니다.''')
    p1.add_argument('--xlsx', required=True)
    p1.add_argument('--store', required=True)
    p1.add_argument('--usage', required=True)
    p1.add_argument('--run-id')
    p1.add_argument('--app-open', action='store_true', help='사용자가 보고/실제 확인한 열람 전제; 잠금 파일만으로 확정 금지')
    p1.add_argument('--procedure', help='Agent가 발견한 명시적 read-only procedure JSON')
    p1.add_argument('--task-mapping', help='현재 업무의 시트·열·시작행 JSON (공유 Skill 아님)')
    p1.add_argument('--confirm-skill', help='명시적으로 실행 확인한 exact digest')
    p1.add_argument('--author', default='local')
    for command in ('review', 'replay', 'publish', 'store-init', 'sync'):
        p = sub.add_parser(command)
        p.add_argument('--store', required=True)
        if command in ('review', 'replay', 'publish'):
            p.add_argument('--id', required=True)
            p.add_argument('--version', required=True)
        if command == 'review':
            p.add_argument('--decision', choices=['approve', 'reject'], required=True)
            p.add_argument('--reviewer', required=True)
        if command == 'replay':
            p.add_argument('--xlsx', required=True)
            p.add_argument('--app-open', action='store_true')
        if command in ('publish', 'store-init', 'sync'):
            p.add_argument('--mirror', required=True)
            p.add_argument('--remote', required=True)
        if command == 'sync':
            p.add_argument('--usage', required=True)
            p.add_argument('--push-usage', action='store_true')
    args = parser.parse_args(argv)
    if args.command in ('run-p1', 'review', 'replay', 'publish', 'store-init', 'sync'):
        return cmd_p1(args)
    if args.command == "run-p0":
        return run_p0()
    if args.command == "apply-requirements":
        return apply_requirements(args.requirements, args.python, args.store, args.usage, args.run_id, args.policy)
    if args.command == "share-export":
        return share_export(args.out)
    if args.command == "share-import":
        return share_import(args.inp)
    if args.command == "status":
        return cmd_status(args.store, args.usage, team=args.team, alias=args.alias)
    if args.command == "match":
        return cmd_match(args.signature, args.target, args.store, args.pip_stderr, args.exit_code)
    if args.command == "dashboard":
        return cmd_dashboard(host=args.host, port=args.port)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
