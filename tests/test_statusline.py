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
    assert "확인 불가" in line
    assert "로컬 Skill 3" in line


def test_published_int_shown():
    line = render_statusline(_snapshot(2, 1, 0, 1))
    assert "게시 2" in line
    assert "상태 미연결" not in line


def test_actual_and_demo_distinguished():
    line = render_statusline(_snapshot(PUBLISHED_UNKNOWN, 2, 5, 1))
    assert "실제 재사용 2" in line
    assert "DEMO 5 제외" in line


def test_top_skill_and_my_contributions():
    top = {"id": "fix-x", "version": "1.0.0", "reuse_count": 4}
    line = render_statusline(_snapshot(PUBLISHED_UNKNOWN, 4, 0, 7, top=top))
    assert "인기 fix-x@1.0.0(재사용 4)" in line
    assert "내 기여(cj) 7" in line


def test_sync_present_vs_absent():
    absent = render_statusline(_snapshot(PUBLISHED_UNKNOWN, 0, 0, 0))
    assert "동기화 없음" in absent
    present = render_statusline(_snapshot(2, 1, 0, 1, synced_at="2026-09-08T00:00:00Z"))
    assert "동기화 2026-09-08T00:00:00Z" in present
