"""U3 V — OrgAggregator(C10) 읽기전용 집계 검증.

소유: CJ. 실제 store/usage(tmp) + 계약7 형태 LifecycleView test 대역으로 검증한다.
lifecycle 미연결 시 추정 금지("상태 조회 미연결"/"확인 불가"), 실적/DEMO 구분, 무쓰기 확인.
"""

import json
import os

from skillloop import descriptor as D
from skillloop import org_aggregator as OA
from skillloop.org_aggregator import PUBLISHED_UNKNOWN, STATE_UNLINKED
from skillloop.store import SkillStore
from skillloop.usage import UsageTracker, build_evidence


def _content(sid, ver, author):
    return {
        "id": sid, "version": ver,
        "origin": {"author": author, "note": "test"},
        "applicability": {"signals": [f"sig:{sid}"]},
        "procedure": {"action": "noop"},
    }


def _seed(tmp_path):
    store = SkillStore(str(tmp_path / "store.json"))
    usage = UsageTracker(str(tmp_path / "usage.json"))
    return store, usage


class FakeLifecycle:
    """계약7(S3.list_lifecycle_states) 형태의 명시적 test 대역."""

    def __init__(self, records):
        self._records = records

    def list_lifecycle_states(self):
        return self._records


def test_distinct_by_digest_and_version(tmp_path):
    store, usage = _seed(tmp_path)
    store.put(D.make_descriptor(_content("skill-a", "1.0.0", "alice")))
    store.put(D.make_descriptor(_content("skill-a", "2.0.0", "alice")))  # 다른 버전=다른 Skill
    snap = OA.build_snapshot(store, usage)
    assert snap["summary"]["distinct_skills_local"] == 2
    assert len(snap["skills"]) == 2


def test_lifecycle_unlinked_is_explicit_not_assumed(tmp_path):
    store, usage = _seed(tmp_path)
    store.put(D.make_descriptor(_content("skill-a", "1.0.0", "alice")))
    snap = OA.build_snapshot(store, usage, lifecycle_view=None)
    # store에 있다는 이유만으로 게시로 집계하지 않는다. 미연결은 0이 아니라 명시 문자열.
    assert snap["summary"]["published_skills"] == PUBLISHED_UNKNOWN
    assert snap["states"] == STATE_UNLINKED


def test_lifecycle_linked_counts_published_from_provider(tmp_path):
    store, usage = _seed(tmp_path)
    d = D.make_descriptor(_content("skill-a", "1.0.0", "alice"))
    store.put(d)
    ref = {"id": d.id, "version": d.version, "digest": d.digest}
    lv = FakeLifecycle([
        {"ref": ref, "lifecycle_state": "PUBLISHED",
         "remote_publish_evidence": {"branch": "team-skill-store"},
         "local_review_evidence": None},
    ])
    snap = OA.build_snapshot(store, usage, lifecycle_view=lv)
    assert snap["summary"]["published_skills"] == 1
    assert isinstance(snap["states"], list) and len(snap["states"]) == 1
    # provider 값 그대로(추정 아님)
    assert snap["states"][0]["lifecycle_state"] == "PUBLISHED"
    assert snap["states"][0]["remote_publish_evidence"] == {"branch": "team-skill-store"}


def test_actual_vs_demo_seed_separated(tmp_path):
    store, usage = _seed(tmp_path)
    real = D.make_descriptor(_content("real-skill", "1.0.0", "alice"))
    demo = D.make_descriptor(_content("demo-skill", "1.0.0", "seed"), demo_seed=True)
    store.put(real)
    store.put(demo)
    # 실제 검증 재사용 1건(digest 포함 → 이벤트 생성), 재사용자 bob
    usage.record_actual_reuse(build_evidence(
        {"id": real.id, "version": real.version, "digest": real.digest},
        {"is_real_success": True}, run_id="r1", reuser_alias="bob"))
    # DEMO 실적은 별도 주입(실제 경로 아님)
    usage.seed_count(demo.id, demo.version, 3)
    snap = OA.build_snapshot(store, usage)
    assert snap["accounting"]["actual_reuses"] == 1
    assert snap["accounting"]["demo_seed_reuses"] == 3


def test_identity_and_cross_reuse(tmp_path):
    store, usage = _seed(tmp_path)
    d = D.make_descriptor(_content("skill-a", "1.0.0", "alice"))
    store.put(d)
    usage.record_actual_reuse(build_evidence(
        {"id": d.id, "version": d.version, "digest": d.digest},
        {"is_real_success": True}, run_id="r1", reuser_alias="bob"))
    snap = OA.build_snapshot(store, usage, my_alias="bob")
    people = {p["alias"]: p for p in snap["people"]}
    assert people["alice"]["contributions"] == 1     # 작성자=origin.author
    assert people["bob"]["cross_reuse"] == 1          # 남의 Skill 재사용
    assert snap["viewer"]["alias"] == "bob"
    assert snap["viewer"]["reuses"] == 1


def test_last_sync_unlinked_marked_local_only(tmp_path):
    store, usage = _seed(tmp_path)
    snap = OA.build_snapshot(store, usage, sync_meta=None)
    assert snap["last_sync"]["synced_at"] is None
    assert "local-only" in snap["last_sync"]["queryable_range"]


def test_read_only_does_not_mutate_files(tmp_path):
    store, usage = _seed(tmp_path)
    d = D.make_descriptor(_content("skill-a", "1.0.0", "alice"))
    store.put(d)
    usage.record_actual_reuse(build_evidence(
        {"id": d.id, "version": d.version, "digest": d.digest},
        {"is_real_success": True}, run_id="r1", reuser_alias="alice"))
    before = os.stat(usage.path).st_mtime_ns, json.load(open(usage.path, encoding="utf-8"))
    OA.build_snapshot(store, usage)
    OA.build_snapshot(store, usage, my_alias="zzz")
    after = os.stat(usage.path).st_mtime_ns, json.load(open(usage.path, encoding="utf-8"))
    assert before[1] == after[1]      # 내용 불변(무쓰기)


class Synced:
    def last_sync(self):
        return {"synced_at": "2026-09-09T00:00:00Z", "branch_revision": "test-commit"}


def _published(d):
    return {"ref": {k: getattr(d, k) for k in ("id", "version", "digest")},
            "lifecycle_state": "PUBLISHED",
            "remote_publish_evidence": {"commit": "test-commit", "branch": "team-skill-store"}}


def test_remote_event_visible_without_local_reuse_and_repeat_is_readonly(tmp_path):
    from skillloop.statusline import render_statusline
    from skillloop.dashboard import render_page
    store, receiver = _seed(tmp_path)
    d = D.make_descriptor(_content("shared", "1", "alice")); store.put(d)
    sender = UsageTracker(str(tmp_path / "sender.json"))
    sender.record_actual_reuse(build_evidence(
        {k: getattr(d, k) for k in ("id", "version", "digest")},
        {"is_real_success": True}, "remote-run", reuser_alias="bob"))
    blob = sender.export_shared_usage()
    assert receiver.import_shared_usage(blob, local_ref_exists=lambda ref: ref == _published(d)["ref"])[0]["applied"]
    assert not receiver.import_shared_usage(blob, local_ref_exists=lambda ref: True)[0]["applied"]
    before = open(receiver.path, "rb").read()
    snap = OA.build_snapshot(store, receiver, FakeLifecycle([_published(d)]), Synced(), my_alias="alice")
    assert snap["accounting"]["actual_reuses"] == 0
    assert snap["organization"]["verified_reuses"] == 1
    assert snap["organization"]["viewer_contributions"] == 1
    text = render_statusline(snap)
    assert "실제 검증 1회" in text and "로컬" not in text
    assert "인기 스킬 - shared@1 · 실제 1회" in text
    assert "우리팀 스킬 적재왕: alice" in text
    assert "팀 게시 Skill 실제 재사용(중복 제외)</th><td>1" in render_page(snap, "/", {})
    assert open(receiver.path, "rb").read() == before


def test_own_event_not_added_twice_and_unpublished_author_not_team_leader(tmp_path):
    store, usage = _seed(tmp_path)
    d = D.make_descriptor(_content("shared", "1", "alice")); store.put(d)
    for i in range(3):store.put(D.make_descriptor(_content(f"candidate-{i}", "1", "bob")))
    usage.record_actual_reuse(build_evidence(_published(d)["ref"], {"is_real_success": True}, "own", reuser_alias="alice"))
    snap = OA.build_snapshot(store, usage, FakeLifecycle([_published(d)]), Synced())
    assert snap["accounting"]["actual_reuses"] == snap["organization"]["verified_reuses"] == 1
    assert snap["organization"]["people"] == [{"alias": "alice", "contributions": 1}]
    unlinked = OA.build_snapshot(store, usage, FakeLifecycle([_published(d)]))
    assert unlinked["organization"]["verified_reuses"] is None
    assert not unlinked["organization"]["available"]


def test_old_digest_version_demo_and_duplicate_events_do_not_inflate_projection(tmp_path):
    from copy import deepcopy
    store, usage = _seed(tmp_path)
    d = D.make_descriptor(_content("shared", "2", "alice")); store.put(d)
    usage.record_actual_reuse(build_evidence(_published(d)["ref"], {"is_real_success": True}, "own", reuser_alias="alice"))
    event = usage.list_shared_events()[0]
    class EventView:
        def current_count(self, *args):return 1
        def list_shared_events(self):
            old_digest=deepcopy(event);old_digest["event_id"]="old-digest";old_digest["skill_ref"]["digest"]="old"
            old_version=deepcopy(event);old_version["event_id"]="old-version";old_version["skill_ref"]["version"]="1"
            demo=deepcopy(event);demo["event_id"]="demo";demo["demo_seed"]=True
            return [event, deepcopy(event), old_digest, old_version, demo]
    old_state=_published(d);old_state["ref"]["digest"]="old"
    snap=OA.build_snapshot(store, EventView(), FakeLifecycle([_published(d), _published(d), old_state]), Synced())
    assert snap["summary"]["published_skills"]==1
    assert snap["organization"]["verified_reuses"]==1
    assert snap["skills"][0]["org_reuse_count"]==1
