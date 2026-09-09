"""U3 V — StatuslineRenderer(C11) 순수 함수 검증.

소유: CJ. 실적/DEMO 구분·내 기여(alias)·lifecycle 미연결 표기를 확인한다.
"""

from skillloop.org_aggregator import PUBLISHED_UNKNOWN
from skillloop.statusline import render_statusline


def _snapshot(published, actual, demo, contributions, top=None, synced_at=None):
    return {
        "summary": {"distinct_skills_local": 3, "published_skills": published},
        "accounting": {"actual_reuses": actual, "demo_seed_reuses": demo},
        "viewer": {"alias": "cj", "contributions": contributions, "reuses": 0},
        "ranking": [top] if top else [],
        "last_sync": {"synced_at": synced_at, "queryable_range": "local-only, 동기화 이력 없음"},
    }


def test_lifecycle_unlinked_shown_not_zero():
    line = render_statusline(_snapshot(PUBLISHED_UNKNOWN, 0, 0, 0))
    assert "상태 미연결" in line
    assert "확인 대기" in line
    assert "로컬 3개" in line


def test_published_int_shown():
    line = render_statusline(_snapshot(2, 1, 0, 1))
    assert "공개 Skill 2개" in line
    assert "상태 미연결" not in line


def test_connected_surface_uses_org_counts_and_published_skills_only():
    snap = _snapshot(1, 99, 20, 8, synced_at="2026-09-09T02:14:08Z")
    snap["skills"] = [{"id": "unpublished-candidate", "version": "1"}]
    snap["organization"] = {
        "available": True, "viewer_contributions": 1, "verified_reuses": 0,
        "people": [{"alias": "cj", "contributions": 1}],
        "ranking": [{"id": "fix-skillloop-demo-pkg-install", "version": "2.0.0", "reuse_count": 0}],
    }
    text = render_statusline(snap)
    assert len(text.splitlines()) == 4
    assert "공개 Skill 1개" in text and "내가 기여한 Skill 1개" in text
    assert "저장된 Skill - python pip 사내환경 적용 방법" in text
    assert "실제 검증 0회" in text and "마지막 동기화" in text
    for hidden in ("로컬", "팀 동기화 확인", "팀 게시 기준", "99회", "20회", "unpublished-candidate", "인기 스킬"):
        assert hidden not in text


def test_actual_and_demo_distinguished():
    line = render_statusline(_snapshot(PUBLISHED_UNKNOWN, 2, 5, 1))
    assert "실제 검증 2회" in line
    assert "데모 기준 5회" in line


def test_top_skill_and_my_contributions():
    top = {"id": "fix-x", "version": "1.0.0", "reuse_count": 4}
    line = render_statusline(_snapshot(PUBLISHED_UNKNOWN, 4, 0, 7, top=top))
    assert "fix-x@1.0.0 · 실제 4회 적용" in line
    assert "내가 기여한 Skill 7개" in line


def test_sync_present_vs_absent():
    absent = render_statusline(_snapshot(PUBLISHED_UNKNOWN, 0, 0, 0))
    assert "동기화 미연결" in absent
    present = render_statusline(_snapshot(2, 1, 0, 1, synced_at="2026-09-08T00:00:00Z"))
    assert "동기화 2026-09-08T00:00:00Z" in present


def test_four_lines_and_untrusted_labels_cannot_inject_controls():
    snap = _snapshot(PUBLISHED_UNKNOWN, 0, 0, 0)
    snap["viewer"]["alias"] = "cj\n\x1b[31m"
    text = render_statusline(snap, team="팀\n이름")
    assert len(text.splitlines()) == 4
    assert "\x1b" not in text
    assert "팀 동기화 확인" not in text


def test_demo_leader_not_presented_as_actual_popularity():
    snap = _snapshot(PUBLISHED_UNKNOWN, 1, 20, 0)
    snap["ranking"] = [
        {"id": "demo", "version": "1", "reuse_count": 20, "demo_seed": True},
        {"id": "real", "version": "1", "reuse_count": 1, "demo_seed": False},
    ]
    text = render_statusline(snap)
    assert "real@1 · 실제 1회" in text
    assert "demo@1" not in text
    assert "데모 기준 20회 + 실제 검증 1회" in text


def test_local_contributor_ties_have_no_invented_team_leader():
    snap = _snapshot(PUBLISHED_UNKNOWN, 0, 0, 0)
    snap["people"] = [{"alias": "b", "contributions": 2}, {"alias": "a", "contributions": 2}]
    text = render_statusline(snap)
    assert "로컬 기여 1위: a, b" in text
    assert "박찬준" not in text


def test_status_cli_context_and_explicit_paths(tmp_path, monkeypatch, capsys):
    import json
    from skillloop import cli
    from skillloop.store import SkillStore
    from skillloop.usage import UsageTracker, build_evidence
    store = tmp_path / "actual-store.json"
    usage = tmp_path / "actual-usage.json"
    cli._seed_store(SkillStore(str(store)))
    d = SkillStore(str(store)).list()[0]
    UsageTracker(str(usage)).record_actual_reuse(build_evidence(
        {"id": d.id, "version": d.version, "digest": d.digest},
        {"is_real_success": True}, "ui-test", reuser_alias="cj"))
    (tmp_path / "skillloop-work.json").write_text(
        json.dumps({"store": store.name, "usage": usage.name}), encoding="utf-8")
    before = (store.read_bytes(), usage.read_bytes())
    monkeypatch.chdir(tmp_path)
    assert cli.main(["status", "--alias", "cj"]) == 0
    output = capsys.readouterr().out
    assert "실제 검증 1회" in output and "| cj" in output
    assert len(output.splitlines()) == 4
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    assert cli.main(["status", "--store", str(store), "--usage", str(usage), "--alias", "cj"]) == 0
    assert "실제 검증 1회" in capsys.readouterr().out
    assert (store.read_bytes(), usage.read_bytes()) == before


def test_project_status_configuration_preserves_settings_and_quotes_paths(tmp_path):
    import importlib.util
    import json
    from pathlib import Path
    import shlex
    spec = importlib.util.spec_from_file_location("work_setup", Path(__file__).with_name("prepare_p0_work.py"))
    setup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(setup)
    settings = tmp_path / ".claude/settings.local.json"
    settings.parent.mkdir()
    settings.write_text('{"permissions": {"allow": ["Read"]}}', encoding="utf-8")
    ctx = {"product_python": str(tmp_path / "runtime space/python.exe"),
           "store": str(tmp_path / "data space/store.json"),
           "usage": str(tmp_path / "data space/usage.json")}
    setup.configure_statusline(tmp_path, ctx)
    result = json.loads(settings.read_text(encoding="utf-8"))
    assert result["permissions"] == {"allow": ["Read"]}
    argv = shlex.split(result["statusLine"]["command"])
    assert argv[0] == Path(ctx["product_python"]).as_posix()
    assert argv[argv.index("--store") + 1] == Path(ctx["store"]).as_posix()


def test_preloaded_inventory_visible_before_first_reuse_without_fake_popularity():
    snap = _snapshot(0, 0, 0, 0)
    snap["skills"] = [{"id": "fix-skillloop-demo-pkg-install", "version": "1.0.0"}]
    text = render_statusline(snap)
    assert "저장된 Skill(로컬) - python pip 사내환경 적용 방법" in text
    assert "공개 Skill 0개" in text
    assert "실제 검증 0회" in text
    assert "인기 스킬" not in text
    assert len(text.splitlines()) == 4


def test_empty_inventory_does_not_invent_preloaded_title():
    snap = _snapshot(0, 0, 0, 0)
    snap["skills"] = []
    text = render_statusline(snap)
    assert "저장된 Skill 없음" in text
    assert "python pip" not in text


def test_stored_untrusted_title_cannot_inject_status_rows():
    snap = _snapshot(0, 0, 0, 0)
    snap["skills"] = [{"id": "unknown", "version": "1"}]
    text = render_statusline(snap, skill_labels={"unknown": "label\n\x1b[31m"})
    assert len(text.splitlines()) == 4
    assert "\x1b" not in text
