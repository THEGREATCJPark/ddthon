"""C11 — read-only four-line Claude status surface. CJ owns this module."""
from __future__ import annotations

from .org_aggregator import PUBLISHED_UNKNOWN


def _label(value: object) -> str:
    """Untrusted labels must not inject terminal controls or extra status rows."""
    return "".join(c for c in str(value) if c.isprintable()).strip()


def render_statusline(snapshot: dict, *, team: str = "디디톤 기술혁신팀",
                      skill_labels: dict | None = None) -> str:
    summary = snapshot.get("summary", {})
    accounting = snapshot.get("accounting", {})
    viewer = snapshot.get("viewer", {})
    sync = snapshot.get("last_sync", {})
    org = snapshot.get("organization", {})
    published = summary.get("published_skills", PUBLISHED_UNKNOWN)
    linked = org.get("available") is True
    connection = "팀 동기화 확인" if linked else "로컬 모드"
    publication = f"{published}개" if isinstance(published, int) else "확인 대기(상태 미연결)"
    alias = _label(viewer.get("alias", "local"))
    lines = [
        f"🧠 SkillLoop · {connection} | 📚 '{_label(team)}' 공개 Skill {publication}"
        f" · 로컬 {summary.get('distinct_skills_local', 0)}개 | {alias}",
        f"✨ 내가 기여한 Skill {org.get('viewer_contributions', 0) if linked else viewer.get('contributions', 0)}개"
        f" ({'팀 게시 기준' if linked else '로컬'})"
        " · 팀에 도움이 될 스킬을 공유해 보세요",
    ]
    people = sorted((p for p in (org.get("people", []) if linked else snapshot.get("people", [])) if p.get("contributions", 0) > 0),
                    key=lambda p: (-p["contributions"], str(p.get("alias", ""))))
    leaders = [p for p in people if p["contributions"] == people[0]["contributions"]] if people else []
    leader = ", ".join(_label(p.get("alias", "")) for p in leaders) or "아직 없음"
    leader_label = f"{'팀 게시' if linked else '로컬'} 기여 1위: {leader}"
    top = next((r for r in (org.get("ranking", []) if linked else snapshot.get("ranking", []))
                if not r.get("demo_seed") and r.get("reuse_count", 0) > 0), None)
    if top:
        title = (skill_labels or {}).get(top["id"], f"{top['id']}@{top['version']}")
        popular = f"{_label(title)} · 실제 {top['reuse_count']}회 적용"
    else:
        popular = "실제 검증 재사용 없음"
    lines.append(f"👑 {leader_label} | 🔥 인기 스킬({'팀' if linked else '로컬'}) - {popular}")
    scope = f"마지막 동기화 {_label(sync['synced_at'])}" if sync.get("synced_at") else "팀 동기화 미연결"
    local = f"데모 기준 {accounting.get('demo_seed_reuses', 0)}회 + 실제 검증 {accounting.get('actual_reuses', 0)}회"
    lines.append((f"팀 실제 검증 {org['verified_reuses']}회 · 로컬 {local}" if linked else f"로컬 {local} · 팀 실적 확인 대기") + f" · {scope}")
    return "\n".join(lines)
