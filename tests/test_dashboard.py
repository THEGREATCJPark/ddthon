"""U3 V — DashboardServer(C12) 읽기전용 검증.

소유: CJ. render_page 순수 검증 + localhost 실서버(포트 0) 통합 검증(외부 네트워크 미의존).
정의된 GET 경로만·비-GET 405·정의외 404·파일 임의 노출 없음·읽기전용(무변경) 확인.
"""

import threading
import urllib.error
import urllib.request

import pytest

from http.server import ThreadingHTTPServer

from skillloop import dashboard as DB
from skillloop.org_aggregator import STATE_UNLINKED


def _snapshot(states=STATE_UNLINKED):
    return {
        "summary": {"distinct_skills_local": 1, "published_skills": "확인 불가",
                    "verified_reuse_events": 1, "reuser_aliases": ["bob"],
                    "contributor_aliases": ["alice"]},
        "scope": {"local": "로컬", "org": "미연결(local-only)"},
        "skills": [{"id": "skill-a", "version": "1.0.0", "digest": "abc",
                    "applicability": {"signals": ["s"]}, "demo_seed": False,
                    "local_reuse_count": 1, "org_reuse_count": 1}],
        "people": [{"alias": "alice", "role": "author", "contributions": 1, "cross_reuse": 0}],
        "states": states,
        "ranking": [{"id": "skill-a", "version": "1.0.0", "reuse_count": 1}],
        "activity": [{"timestamp": "2026-09-08T00:00:00Z",
                      "skill_ref": {"id": "skill-a", "version": "1.0.0"}, "reuser_alias": "bob"}],
        "last_sync": {"synced_at": None, "queryable_range": "local-only, 동기화 이력 없음"},
        "accounting": {"actual_reuses": 1, "demo_seed_reuses": 0},
        "viewer": {"alias": "local", "contributions": 0, "reuses": 0},
    }


# --- render_page 순수 검증 ---

def test_render_overview_and_pages():
    snap = _snapshot()
    assert "요약" in DB.render_page(snap, "/", {})
    assert "skill-a" in DB.render_page(snap, "/skills", {})
    assert "Skill 상세" in DB.render_page(snap, "/skill", {"id": ["skill-a"], "version": ["1.0.0"]})
    assert "alice" in DB.render_page(snap, "/people", {})
    assert "bob" in DB.render_page(snap, "/activity", {})


def test_render_unknown_path_raises():
    with pytest.raises(KeyError):
        DB.render_page(_snapshot(), "/secret", {})


def test_lifecycle_unlinked_message_on_overview():
    html = DB.render_page(_snapshot(states=STATE_UNLINKED), "/", {})
    assert STATE_UNLINKED in html
    assert "계약7" in html   # 미연결 사유를 명시


def test_remote_publish_only_when_evidence_present():
    linked = _snapshot(states=[
        {"ref": {"id": "skill-a", "version": "1.0.0"}, "lifecycle_state": "REVIEW",
         "remote_publish_evidence": None, "local_review_evidence": None},
    ])
    html = DB.render_page(linked, "/", {})
    # 로컬 검토 기록 없음만으로 "원격 게시(근거 있음)"라고 하지 않는다.
    assert "원격 게시 근거 없음" in html
    assert "원격 게시(근거 있음)" not in html


def test_skills_search_filter():
    snap = _snapshot()
    snap["skills"].append({"id": "other", "version": "1.0.0", "digest": "d",
                           "applicability": {}, "demo_seed": False,
                           "local_reuse_count": 0, "org_reuse_count": 0})
    html = DB.render_page(snap, "/skills", {"q": ["skill-a"]})
    assert "skill-a" in html and "other" not in html


# --- localhost 실서버 통합 검증(포트 0, 외부 네트워크 미의존) ---

@pytest.fixture()
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), DB._make_handler(_snapshot))
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield port
    httpd.shutdown()
    httpd.server_close()


def _get(port, path, method="GET"):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method)
    return urllib.request.urlopen(req, timeout=5)


def test_get_root_returns_html(server):
    resp = _get(server, "/")
    assert resp.status == 200
    body = resp.read().decode("utf-8")
    assert "SkillLoop 조직 대시보드" in body


def test_unknown_path_404(server):
    with pytest.raises(urllib.error.HTTPError) as e:
        _get(server, "/etc/passwd")
    assert e.value.code == 404


def test_traversal_path_not_served(server):
    # 파일 임의 노출 금지: 정의 외 경로는 404(파일 시스템 접근 없음).
    with pytest.raises(urllib.error.HTTPError) as e:
        _get(server, "/../skillloop/cli.py")
    assert e.value.code == 404


def test_non_get_method_405(server):
    with pytest.raises(urllib.error.HTTPError) as e:
        _get(server, "/", method="POST")
    assert e.value.code == 405
