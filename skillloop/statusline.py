"""C11 — read-only four-line Claude status surface. CJ owns this module."""
from __future__ import annotations

from .org_aggregator import PUBLISHED_UNKNOWN

SKILL_LABELS = {
    "fix-skillloop-demo-pkg-install": "python pip 사내환경 적용 방법",
    "file-access-8738e696cff8bbb20c98": "NASCA 환경 Excel 읽기 방법",
}


def skill_title(skill_id: str, version: str, labels: dict | None = None) -> str:
    return _label((labels or {}).get(skill_id, SKILL_LABELS.get(skill_id, f"{skill_id}@{version}")))


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
    connection = "" if linked else " · 로컬 모드"
    local_count = "" if linked else f" · 로컬 {summary.get('distinct_skills_local', 0)}개"
    publication = f"{published}개" if isinstance(published, int) else "확인 대기(상태 미연결)"
    alias = _label(viewer.get("alias", "local"))
    lines = [
        f"🧠 SkillLoop{connection} | 📚 '{_label(team)}' 공개 Skill {publication}"
        f"{local_count} | {alias}",
        f"✨ 내가 기여한 Skill {org.get('viewer_contributions', 0) if linked else viewer.get('contributions', 0)}개"
        + ("" if linked else " (로컬)")
        + " · 팀에 도움이 될 스킬을 공유해 보세요",
    ]
    people = sorted((p for p in (org.get("people", []) if linked else snapshot.get("people", [])) if p.get("contributions", 0) > 0),
                    key=lambda p: (-p["contributions"], str(p.get("alias", ""))))
    leaders = [p for p in people if p["contributions"] == people[0]["contributions"]] if people else []
    leader = ", ".join("작성자 미등록" if p.get("alias") in (None, "", "local")
                       else _label(p["alias"]) for p in leaders) or "아직 없음"
    leader_label = f"우리팀 스킬 적재왕: {leader}" if linked else f"로컬 기여 1위: {leader}"
    top = next((r for r in (org.get("ranking", []) if linked else snapshot.get("ranking", []))
                if not r.get("demo_seed") and r.get("reuse_count", 0) > 0), None)
    if top:
        title = skill_title(top["id"], top["version"], skill_labels)
        popular = f"{_label(title)} · 실제 {top['reuse_count']}회 적용"
        skill_summary = f"🔥 인기 스킬{'' if linked else '(로컬)'} - {popular}"
    else:
        stored = sorted(org.get("ranking", []) if linked else snapshot.get("skills", []),
                        key=lambda s: (not bool((skill_labels or SKILL_LABELS).get(s["id"])), s["id"], s["version"]))
        if stored:
            first = stored[0]
            title = skill_title(first["id"], first["version"], skill_labels)
            remainder = f" 외 {len(stored) - 1}개" if len(stored) > 1 else ""
            skill_summary = f"📖 저장된 Skill{'' if linked else '(로컬)'} - {title}{remainder} · 실제 검증 재사용 없음"
        else:
            skill_summary = "📖 저장된 Skill 없음 · 실제 검증 재사용 없음"
    lines.append(f"👑 {leader_label} | {skill_summary}")
    scope = f"마지막 동기화 {_label(sync['synced_at'])}" if sync.get("synced_at") else "팀 동기화 미연결"
    local = f"데모 기준 {accounting.get('demo_seed_reuses', 0)}회 + 실제 검증 {accounting.get('actual_reuses', 0)}회"
    lines.append((f"실제 검증 {org['verified_reuses']}회" if linked else f"로컬 {local} · 팀 실적 확인 대기") + f" · {scope}")
    return "\n".join(lines)
