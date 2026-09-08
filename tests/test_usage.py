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
