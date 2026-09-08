"""C11 — StatuslineRenderer: OrgSnapshot → 상태줄 한 줄 문자열.

소유(단일 수정자): CJ (U3)
계약(U3 최소 설계 §2.2): render_statusline(snapshot) -> str

성격: **순수 함수**(I/O·상태 변경 없음). C10 스냅샷만 소비.
표시(FR-UI-1): 조직 Skill 수 · 내 기여 · 인기 Skill · 재사용 현황.
    - 실제 검증 실적과 DEMO_SEED를 구분(FR-USAGE-3).
    - lifecycle 미연결·동기화 미연결을 추정 없이 명시.
"""

from __future__ import annotations

from .org_aggregator import PUBLISHED_UNKNOWN


def render_statusline(snapshot: dict) -> str:
    """스냅샷을 상태줄용 한 줄로 렌더링(비-ASCII 포함, 표시 전용)."""
    summary = snapshot.get("summary", {})
    accounting = snapshot.get("accounting", {})
    viewer = snapshot.get("viewer", {})
    ranking = snapshot.get("ranking", [])
    last_sync = snapshot.get("last_sync", {})

    distinct = summary.get("distinct_skills_local", 0)
    published = summary.get("published_skills", PUBLISHED_UNKNOWN)
    actual = accounting.get("actual_reuses", 0)
    demo = accounting.get("demo_seed_reuses", 0)

    parts = [f"SkillLoop"]
    parts.append(f"로컬 Skill {distinct}")

    # 게시 수: lifecycle 미연결이면 "확인불가(상태 미연결)"로 명시(0 추정 금지).
    if isinstance(published, int):
        parts.append(f"게시 {published}")
    else:
        parts.append(f"게시 {published}(상태 미연결)")

    alias = viewer.get("alias", "local")
    parts.append(f"내 기여({alias}) {viewer.get('contributions', 0)}")

    # 인기 Skill(실제 검증 재사용 1위).
    top = next((r for r in ranking if r.get("reuse_count", 0) > 0), None)
    if top is not None:
        parts.append(f"인기 {top['id']}@{top['version']}(재사용 {top['reuse_count']})")
    else:
        parts.append("인기 없음")

    reuse_str = f"실제 재사용 {actual}"
    if demo:
        reuse_str += f"(DEMO {demo} 제외)"
    parts.append(reuse_str)

    qrange = last_sync.get("queryable_range", "")
    if last_sync.get("synced_at"):
        parts.append(f"동기화 {last_sync['synced_at']}")
    else:
        parts.append(f"동기화 없음({qrange})")

    return " | ".join(parts)
