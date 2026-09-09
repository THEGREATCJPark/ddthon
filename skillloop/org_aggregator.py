"""C10 — OrgAggregator: 읽기전용 조직 스냅샷 집계(단일 read-model).

소유(단일 수정자): CJ (U3)
계약(U3 최소 설계 §2.1, §4):
    - build_snapshot(store, usage, lifecycle_view=None, sync_meta=None,
                     my_alias="local") -> OrgSnapshot(dict)

성격: **읽기전용 파생.** store/usage/lifecycle 소유 상태를 수정하지 않는다.
상태줄(C11)·대시보드(C12)가 **동일 OrgSnapshot**을 소비한다(FR-UI-3).

정직성 규칙(구현 기준, 재승인 대상 아님):
    - lifecycle 상태는 **`LifecycleView`(계약7 형태) provider로만** 읽는다.
      미연결(provider=None)이면 states="상태 조회 미연결", published_skills="확인 불가"로
      표시하고 0건·특정 상태로 **추정하지 않는다.** store를 직접 읽는 임시 우회는 만들지 않는다.
    - store에 있다는 이유만으로 "게시(PUBLISHED)"로 집계하지 않는다(로컬 저장 ≠ 조직 게시).
    - 로컬 검토 기록이 없다는 사실만으로 "원격 게시"라고 판단하지 않는다.
      실제 remote_publish_evidence가 있을 때만 원격 게시로 표시한다(표시는 C11/C12).
    - 로컬 조회 결과(로컬 store·usage)와 원격 동기화된 조직 현황(events·lifecycle·last_sync)을
      구분한다. 미연결 lifecycle/last_sync만 명시적으로 표시한다.
    - 실제 검증 실적과 DEMO_SEED를 구분한다(descriptor.demo_seed 기준, FR-USAGE-3).
    - secret·원본 데이터·procedure 내부는 스냅샷에 포함하지 않는다(NFR-SEC-1).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

# lifecycle 미연결 표식(문자열 상수). 0·특정 상태로 추정하지 않기 위한 명시적 값.
STATE_UNLINKED = "상태 조회 미연결"
PUBLISHED_UNKNOWN = "확인 불가"


@runtime_checkable
class LifecycleView(Protocol):
    """계약7 형태의 S3 읽기전용 상태 조회 인터페이스(실구현은 B/U2, U3는 주입만).

    반환 각 항목: {ref{id,version,digest}, lifecycle_state,
                   local_review_evidence, remote_publish_evidence}
    """

    def list_lifecycle_states(self) -> list[dict]:
        ...


@runtime_checkable
class SyncMeta(Protocol):
    """C4(gitsync.py, B 소유) last_sync 형태(실구현은 B, U3는 주입만)."""

    def last_sync(self) -> dict | None:
        ...


def _author_of(descriptor) -> str:
    origin = getattr(descriptor, "origin", None) or {}
    return origin.get("author", "unknown")


def build_snapshot(store, usage, lifecycle_view: LifecycleView | None = None,
                   sync_meta: SyncMeta | None = None, my_alias: str = "local") -> dict:
    """로컬 store·usage(+주입된 lifecycle/last_sync)로 단일 OrgSnapshot을 만든다(읽기전용).

    provider(lifecycle_view/sync_meta)가 None이면 해당 영역을 '미연결'로 명시하고
    나머지 로컬 실데이터 집계는 그대로 수행한다(이 결정으로 U3를 대기시키지 않는다).
    """
    descriptors = store.list()
    exact_descriptors = {(d.id, d.version, d.digest): d for d in descriptors}
    # C3 owns validation/dedup. This read-only projection also excludes obsolete refs
    # and never adds the local counter to the same event already present in C3.
    events_by_id = {}
    for event in usage.list_shared_events():
        ref = event.get("skill_ref", {})
        key = (ref.get("id"), ref.get("version"), ref.get("digest"))
        d = exact_descriptors.get(key)
        if (d is not None and not d.demo_seed and not event.get("demo_seed")
                and event.get("event_id")
                and event.get("evidence", {}).get("is_real_success") is True):
            events_by_id.setdefault(event["event_id"], event)
    events = list(events_by_id.values())
    event_counts = {}
    for event in events:
        ref = event["skill_ref"]
        key = (ref["id"], ref["version"], ref["digest"])
        event_counts[key] = event_counts.get(key, 0) + 1

    # --- 로컬 저장 Skill(dedup: 서로 다른 digest 기준, FR-ORG-1) ---
    seen_digests: set[str] = set()
    skills: list[dict] = []
    contributor_aliases: set[str] = set()
    author_by_ref: dict[tuple[str, str], str] = {}
    actual_reuses = 0
    demo_seed_reuses = 0
    for d in descriptors:
        local_reuse = usage.current_count(d.id, d.version)
        org_reuse = event_counts.get((d.id, d.version, d.digest), 0)
        author = _author_of(d)
        contributor_aliases.add(author)
        author_by_ref[(d.id, d.version)] = author
        if getattr(d, "demo_seed", False):
            demo_seed_reuses += local_reuse
        else:
            actual_reuses += local_reuse
        skills.append({
            "id": d.id,
            "version": d.version,
            "digest": d.digest,
            "applicability": d.applicability,     # 비민감 신호만(procedure 미포함)
            "demo_seed": bool(getattr(d, "demo_seed", False)),
            "local_reuse_count": local_reuse,
            "org_reuse_count": org_reuse,
        })
        seen_digests.add(d.digest)

    # --- 공유 재사용 이벤트(조직 집계 대상; event_id dedup은 C3 소유) ---
    reuser_aliases = sorted({ev.get("reuser_alias", "") for ev in events if ev.get("reuser_alias")})

    # people: 작성자(origin) + 재사용자(alias). cross_reuse = 자신이 작성하지 않은 Skill 재사용.
    people: dict[str, dict] = {}
    for author in contributor_aliases:
        people.setdefault(author, {"alias": author, "role": "author",
                                   "contributions": 0, "cross_reuse": 0})
    for (rid, rver), author in author_by_ref.items():
        people[author]["contributions"] += 1
    for ev in events:
        alias = ev.get("reuser_alias", "")
        if not alias:
            continue
        p = people.setdefault(alias, {"alias": alias, "role": "reuser",
                                      "contributions": 0, "cross_reuse": 0})
        ref = ev.get("skill_ref", {})
        skill_author = author_by_ref.get((ref.get("id"), ref.get("version")))
        if skill_author is not None and skill_author != alias:
            p["cross_reuse"] += 1

    # ranking: 실제 검증 재사용(local_reuse_count) 내림차순, 동점 시 id 오름차순(결정적).
    ranking = sorted(
        ({"id": s["id"], "version": s["version"], "reuse_count": s["local_reuse_count"],
          "demo_seed": s["demo_seed"]} for s in skills),
        key=lambda r: (-r["reuse_count"], r["id"]),
    )

    # activity: 이벤트를 timestamp 내림차순(최근 우선). timestamp 없으면 뒤로.
    activity = sorted(
        ({"timestamp": ev.get("timestamp", ""), "skill_ref": ev.get("skill_ref", {}),
          "reuser_alias": ev.get("reuser_alias", "")} for ev in events),
        key=lambda a: a["timestamp"], reverse=True,
    )

    # --- lifecycle 상태(계약7 provider로만; 미연결이면 명시) ---
    if lifecycle_view is None:
        raw_states = []
        states: object = STATE_UNLINKED
        published_skills: object = PUBLISHED_UNKNOWN
        lifecycle_linked = False
    else:
        raw_states = lifecycle_view.list_lifecycle_states()
        states = [
            {
                "ref": rec.get("ref", {}),
                "lifecycle_state": rec.get("lifecycle_state"),
                "local_review_evidence": rec.get("local_review_evidence"),
                "remote_publish_evidence": rec.get("remote_publish_evidence"),
            }
            for rec in raw_states
        ]
        published_skills = len({tuple(rec.get("ref", {}).get(k) for k in ("id", "version", "digest"))
                                for rec in raw_states if rec.get("lifecycle_state") == "PUBLISHED"}
                               & exact_descriptors.keys())
        lifecycle_linked = True

    # --- last_sync(C4 provider로만; 미연결이면 local-only 명시) ---
    if sync_meta is None:
        last_sync = {"synced_at": None, "branch_revision": None,
                     "queryable_range": "local-only, 동기화 이력 없음"}
    else:
        ls = sync_meta.last_sync() or {}
        last_sync = {
            "synced_at": ls.get("synced_at"),
            "branch_revision": ls.get("branch_revision"),
            "remote": ls.get("remote"),
            "branch": ls.get("branch"),
            "queryable_range": ls.get("queryable_range", "synced"),
        }

    viewer_contrib = people.get(my_alias, {}).get("contributions", 0)
    viewer_reuse = sum(1 for ev in events if ev.get("reuser_alias") == my_alias)

    org_available = lifecycle_linked and bool(last_sync.get("synced_at"))
    from .publish_pipeline import remote_matches
    transport_context = last_sync if last_sync.get("remote") else None
    published_refs = {
        tuple(rec.get("ref", {}).get(k) for k in ("id", "version", "digest"))
        for rec in raw_states
        if rec.get("lifecycle_state") == "PUBLISHED"
        and (rec.get("remote_publish_evidence") or {}).get("commit")
        and remote_matches(rec.get("remote_publish_evidence") or {}, transport_context)
    } & exact_descriptors.keys()
    org_people = {}
    org_ranking = []
    for ref in sorted(published_refs):
        d = exact_descriptors[ref]
        if d.demo_seed:
            continue
        author = _author_of(d)
        org_people[author] = org_people.get(author, 0) + 1
        org_ranking.append({"id": d.id, "version": d.version, "digest": d.digest,
                            "reuse_count": event_counts.get(ref, 0), "demo_seed": False})
    org_ranking.sort(key=lambda r: (-r["reuse_count"], r["id"], r["version"], r["digest"]))
    organization = {
        "available": org_available,
        "basis": "마지막 동기화 후 로컬에 관찰된 게시 Skill·검증 이벤트 (실시간 전체 조직 아님)",
        "verified_reuses": sum(r["reuse_count"] for r in org_ranking) if org_available else None,
        "ranking": org_ranking if org_available else [],
        "people": [{"alias": a, "contributions": n} for a, n in sorted(org_people.items())] if org_available else [],
        "viewer_contributions": org_people.get(my_alias, 0) if org_available else None,
    }

    return {
        "summary": {
            "distinct_skills_local": len(seen_digests),
            "published_skills": published_skills,     # lifecycle 미연결이면 "확인 불가"
            "verified_reuse_events": len(events),
            "reuser_aliases": reuser_aliases,
            "contributor_aliases": sorted(contributor_aliases),
        },
        "scope": {
            "local": "로컬 store·usage 기준(항상 가용)",
            "org": "동기화된 events·lifecycle 기준" if lifecycle_linked
                   else "미연결(local-only) — lifecycle/last_sync 연결 후 조직 현황 반영",
        },
        "skills": skills,                 # 로컬 저장 Skill(조직 게시와 별개)
        "people": sorted(people.values(), key=lambda p: p["alias"]),
        "states": states,                 # provider 값 그대로 / 미연결이면 문자열
        "ranking": ranking,
        "activity": activity,
        "last_sync": last_sync,
        "organization": organization,
        "accounting": {                   # FR-USAGE-3: 실제 실적 vs DEMO_SEED
            "actual_reuses": actual_reuses,
            "demo_seed_reuses": demo_seed_reuses,
        },
        "viewer": {                       # 상태줄 "내 기여" 표시용(alias 기준)
            "alias": my_alias,
            "contributions": viewer_contrib,
            "reuses": viewer_reuse,
        },
    }
