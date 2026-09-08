"""V9, V10, V11 — C3 단독 카운트·run_id 실행 dedup·사전적재 실적 반영. 소유: CJ. 구현: S4."""

from skillloop import usage as U
from skillloop.usage import UsageTracker

REF = {"id": "pkg-fix", "version": "1.0.0"}


def _ev(run_id, is_real=True, demo=False):
    return U.build_evidence(
        REF, {"is_real_success": is_real, "pip_exit_code": 0}, run_id, demo_seed=demo
    )


def test_only_real_success_increments_count(tmp_path):
    # V9: 실제 성공만 +1. 실패는 카운트 없음.
    t = UsageTracker(str(tmp_path / "usage.json"))
    rid = U.new_execution_id()
    r = t.record_actual_reuse(_ev(rid, is_real=False))
    assert r.counted is False and r.new_count == 0 and r.reason == "not-real-success"
    r2 = t.record_actual_reuse(_ev(U.new_execution_id(), is_real=True))
    assert r2.counted is True and r2.new_count == 1


def test_same_run_id_does_not_double_count(tmp_path):
    # V10: 동일 실행(같은 run_id) 재검증·재시작은 중복 +1 방지.
    t = UsageTracker(str(tmp_path / "usage.json"))
    rid = U.new_execution_id()
    assert t.record_actual_reuse(_ev(rid)).counted is True
    again = t.record_actual_reuse(_ev(rid))
    assert again.counted is False and again.reason == "same-execution"
    assert t.current_count("pkg-fix", "1.0.0") == 1


def test_new_execution_ids_each_increment(tmp_path):
    # V10: 같은 문제의 다른 실행(새 run_id)은 각각 +1.
    t = UsageTracker(str(tmp_path / "usage.json"))
    assert t.record_actual_reuse(_ev(U.new_execution_id())).new_count == 1
    assert t.record_actual_reuse(_ev(U.new_execution_id())).new_count == 2


def test_new_execution_id_unique():
    assert U.new_execution_id() != U.new_execution_id()


def test_demo_seed_excluded_from_actual_count(tmp_path):
    # V11 경계: 미리 만든 실적(demo_seed=True)은 실제 카운트에 반영 안 됨.
    t = UsageTracker(str(tmp_path / "usage.json"))
    r = t.record_actual_reuse(_ev(U.new_execution_id(), demo=True))
    assert r.counted is False and r.reason == "demo-seed"


def test_preloaded_skill_reuse_counts_when_not_demo_seed(tmp_path):
    # V11: 사전 적재 Skill(demo_seed=False)의 실제 재사용 성공은 실적 반영.
    t = UsageTracker(str(tmp_path / "usage.json"))
    t.seed_count("pkg-fix", "1.0.0", 7)   # 미리 만든 실적 주입(시연)
    r = t.record_actual_reuse(_ev(U.new_execution_id(), is_real=True, demo=False))
    assert r.counted is True and r.new_count == 8


def test_persistence_across_instances(tmp_path):
    # seen_run_ids·counts 영속화: 재시작(새 인스턴스) 후에도 dedup 유지.
    p = str(tmp_path / "usage.json")
    rid = U.new_execution_id()
    t1 = UsageTracker(p)
    assert t1.record_actual_reuse(_ev(rid)).counted is True
    t2 = UsageTracker(p)  # 재시작 시뮬레이션
    again = t2.record_actual_reuse(_ev(rid))
    assert again.counted is False and again.reason == "same-execution"
    assert t2.current_count("pkg-fix", "1.0.0") == 1


# --- C-d: 공유 재사용 이벤트(VERIFIED_REUSE) ---

REF_D = {"id": "pkg-fix", "version": "1.0.0", "digest": "a" * 64}  # 정확한 참조(digest 포함)


def _ev_d(run_id, is_real=True, demo=False, alias="local", ref=None):
    return U.build_evidence(
        ref if ref is not None else REF_D,
        {"is_real_success": is_real, "pip_exit_code": 0},
        run_id, demo_seed=demo, reuser_alias=alias,
    )


def test_event_created_only_when_counted_with_digest(tmp_path):
    # counted=True + digest 있는 참조일 때만 이벤트 생성.
    t = UsageTracker(str(tmp_path / "usage.json"))
    t.record_actual_reuse(_ev_d(U.new_execution_id()))
    assert t.shared_reuse_count("pkg-fix", "1.0.0") == 1


def test_no_event_without_digest_no_backfill(tmp_path):
    # 기존 카운트 역산 금지: digest 없는 evidence는 카운트되어도 이벤트 미생성.
    t = UsageTracker(str(tmp_path / "usage.json"))
    r = t.record_actual_reuse(_ev(U.new_execution_id()))  # REF(no digest)
    assert r.counted is True
    assert t.shared_reuse_count("pkg-fix", "1.0.0") == 0
    # export도 비어 있음(성공 근거 역산 없음)
    import json
    assert json.loads(t.export_shared_usage().decode("utf-8"))["events"] == []


def test_not_counted_creates_no_event(tmp_path):
    # 실패·demo·동일 run_id는 카운트 안 되므로 이벤트도 없음.
    t = UsageTracker(str(tmp_path / "usage.json"))
    t.record_actual_reuse(_ev_d(U.new_execution_id(), is_real=False))
    t.record_actual_reuse(_ev_d(U.new_execution_id(), demo=True))
    assert t.shared_reuse_count("pkg-fix", "1.0.0") == 0


def test_event_id_deterministic_and_stable():
    # 같은 (skill_ref, run_id, alias) → 같은 event_id(재전송 dedup 키).
    rid = "run-1"
    a = U.compute_event_id(REF_D, rid, "local")
    b = U.compute_event_id(REF_D, rid, "local")
    c = U.compute_event_id(REF_D, rid, "other")  # alias 다르면 다른 이벤트
    assert a == b and a != c


def test_export_import_roundtrip_dedup(tmp_path):
    # A가 만든 이벤트 → B로 export/import → 반영 1회. 재import는 dedup.
    src = UsageTracker(str(tmp_path / "src.json"))
    src.record_actual_reuse(_ev_d(U.new_execution_id()))
    blob = src.export_shared_usage()

    dst = UsageTracker(str(tmp_path / "dst.json"))
    r1 = dst.import_shared_usage(blob, local_ref_exists=lambda ref: True)
    assert [x["applied"] for x in r1] == [True]
    assert dst.shared_reuse_count("pkg-fix", "1.0.0") == 1
    # 같은 blob 재import → 전부 dedup(추가 집계 없음)
    r2 = dst.import_shared_usage(blob, local_ref_exists=lambda ref: True)
    assert [x["reason"] for x in r2] == ["dedup"]
    assert dst.shared_reuse_count("pkg-fix", "1.0.0") == 1


def test_import_requires_local_ref_exists(tmp_path):
    # VERIFIED_REUSE: 정확한 Skill이 로컬에 없으면 반영 거부.
    src = UsageTracker(str(tmp_path / "src.json"))
    src.record_actual_reuse(_ev_d(U.new_execution_id()))
    blob = src.export_shared_usage()
    dst = UsageTracker(str(tmp_path / "dst.json"))
    r = dst.import_shared_usage(blob, local_ref_exists=lambda ref: False)
    assert [x["reason"] for x in r] == ["not-local"]
    assert dst.shared_reuse_count("pkg-fix", "1.0.0") == 0


def test_own_event_returning_does_not_reaggregate(tmp_path):
    # 로컬에서 이미 집계한 이벤트가 왕복해 돌아와도 추가 집계 안 함(event_id dedup).
    t = UsageTracker(str(tmp_path / "usage.json"))
    t.record_actual_reuse(_ev_d(U.new_execution_id()))
    own_blob = t.export_shared_usage()  # 자기 이벤트
    before = t.shared_reuse_count("pkg-fix", "1.0.0")
    t.import_shared_usage(own_blob, local_ref_exists=lambda ref: True)
    assert t.shared_reuse_count("pkg-fix", "1.0.0") == before  # 불변


def test_import_does_not_change_local_counts(tmp_path):
    # import는 로컬 재사용 카운트(counts)를 바꾸지 않는다(조직 실적=events).
    src = UsageTracker(str(tmp_path / "src.json"))
    src.record_actual_reuse(_ev_d(U.new_execution_id(), alias="peer"))
    blob = src.export_shared_usage()
    dst = UsageTracker(str(tmp_path / "dst.json"))
    dst.import_shared_usage(blob, local_ref_exists=lambda ref: True)
    assert dst.current_count("pkg-fix", "1.0.0") == 0       # counts 불변
    assert dst.shared_reuse_count("pkg-fix", "1.0.0") == 1   # events는 1
