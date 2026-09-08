"""C12 — DashboardServer: OrgSnapshot → localhost 읽기전용 대시보드.

소유(단일 수정자): CJ (U3)
계약(U3 최소 설계 §2.3): serve_readonly(snapshot_provider, host="127.0.0.1", port) -> None

성격·제약(FR-UI-2, NFR-SEC-2, 결정2):
    - Python 표준 라이브러리 http.server만 사용(외부 프레임워크·라이브러리 없음).
    - 127.0.0.1 바인딩. **정의된 GET 경로만** 처리(/, /skills, /skill, /people, /activity).
    - **정적 파일 서빙·디렉터리 리스팅 없음** — 프로젝트 파일 임의 노출 금지.
    - 정의 외 경로 → 404, 비-GET 메서드 → 405. 쓰기·승인·게시 엔드포인트 없음.
    - 상태줄과 **동일 OrgSnapshot**을 소비. lifecycle 미연결·실적/DEMO 구분 유지.
    - render_page는 순수 함수(스냅샷+경로+쿼리 → HTML). secret·원본·procedure 미노출.
"""

from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .org_aggregator import PUBLISHED_UNKNOWN, STATE_UNLINKED

# 정의된 GET 경로만 허용(그 외 404). 파일 경로·디렉터리는 처리 대상이 아니다.
ALLOWED_PATHS = {"/", "/skills", "/skill", "/people", "/activity"}


def _esc(v: object) -> str:
    return html.escape(str(v), quote=True)


def _layout(title: str, body: str, snapshot: dict) -> str:
    ls = snapshot.get("last_sync", {})
    scope = snapshot.get("scope", {})
    banner = (
        f"<div class='meta'>범위: 로컬={_esc(scope.get('local',''))} · "
        f"조직={_esc(scope.get('org',''))} · "
        f"동기화={_esc(ls.get('synced_at') or ls.get('queryable_range',''))}</div>"
    )
    nav = (
        "<nav><a href='/'>요약</a> · <a href='/skills'>Skill</a> · "
        "<a href='/people'>사람</a> · <a href='/activity'>활동</a></nav>"
    )
    return (
        "<!DOCTYPE html><html lang='ko'><head><meta charset='utf-8'>"
        f"<title>{_esc(title)}</title>"
        "<style>body{font-family:system-ui,sans-serif;margin:2rem;max-width:60rem}"
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:.3rem .5rem;text-align:left}"
        ".meta{color:#555;font-size:.9rem;margin:.5rem 0}.demo{color:#a60}nav a{margin-right:.3rem}</style>"
        f"</head><body><h1>SkillLoop 조직 대시보드 <small>(읽기전용)</small></h1>{nav}{banner}{body}"
        "</body></html>"
    )


def _render_overview(snapshot: dict) -> str:
    s = snapshot.get("summary", {})
    acc = snapshot.get("accounting", {})
    published = s.get("published_skills", PUBLISHED_UNKNOWN)
    pub_str = str(published) if isinstance(published, int) else f"{published}(상태 미연결)"
    rows = [
        ("로컬 저장 Skill(디스크립터 수)", s.get("distinct_skills_local", 0)),
        ("조직 게시(PUBLISHED)", pub_str),
        ("검증 재사용 이벤트(dedup)", s.get("verified_reuse_events", 0)),
        ("실제 재사용 합계", acc.get("actual_reuses", 0)),
        ("DEMO_SEED(실적 제외)", acc.get("demo_seed_reuses", 0)),
        ("기여자", ", ".join(s.get("contributor_aliases", [])) or "-"),
        ("재사용자", ", ".join(s.get("reuser_aliases", [])) or "-"),
    ]
    body = "<h2>요약</h2><table>" + "".join(
        f"<tr><th>{_esc(k)}</th><td>{_esc(v)}</td></tr>" for k, v in rows
    ) + "</table>"
    body += _render_states_block(snapshot)
    return body


def _render_states_block(snapshot: dict) -> str:
    states = snapshot.get("states")
    if states == STATE_UNLINKED or not isinstance(states, list):
        return ("<h2>게시/검토 상태</h2>"
                f"<p class='meta'>{_esc(STATE_UNLINKED)} — S3 상태 조회 계약(계약7) 연결 후 표시됩니다. "
                "0건·특정 상태로 추정하지 않습니다.</p>")
    if not states:
        return "<h2>게시/검토 상태</h2><p class='meta'>상태 레코드 없음(연결됨).</p>"
    rows = []
    for rec in states:
        ref = rec.get("ref", {})
        # 원격 게시는 실제 remote_publish_evidence가 있을 때만 표시(추정 금지).
        remote = rec.get("remote_publish_evidence")
        local = rec.get("local_review_evidence")
        remote_str = "원격 게시(근거 있음)" if remote else "원격 게시 근거 없음"
        local_str = "로컬 검토 기록 있음" if local else "로컬 검토 기록 없음"
        rows.append(
            f"<tr><td>{_esc(ref.get('id'))}@{_esc(ref.get('version'))}</td>"
            f"<td>{_esc(rec.get('lifecycle_state'))}</td>"
            f"<td>{_esc(remote_str)}</td><td>{_esc(local_str)}</td></tr>"
        )
    return ("<h2>게시/검토 상태</h2><table>"
            "<tr><th>Skill</th><th>상태</th><th>원격</th><th>로컬</th></tr>"
            + "".join(rows) + "</table>")


def _render_skills(snapshot: dict, q: str = "") -> str:
    skills = snapshot.get("skills", [])
    if q:
        ql = q.lower()
        skills = [s for s in skills if ql in s["id"].lower()]
    rows = []
    for s in skills:
        demo = " <span class='demo'>[DEMO]</span>" if s.get("demo_seed") else ""
        rows.append(
            f"<tr><td><a href='/skill?id={_esc(s['id'])}&version={_esc(s['version'])}'>"
            f"{_esc(s['id'])}</a>{demo}</td><td>{_esc(s['version'])}</td>"
            f"<td>{_esc(s['local_reuse_count'])}</td><td>{_esc(s['org_reuse_count'])}</td></tr>"
        )
    search = (f"<form method='get' action='/skills'>"
              f"<input name='q' value='{_esc(q)}' placeholder='id 검색'>"
              f"<button type='submit'>검색</button></form>")
    table = ("<table><tr><th>Skill(로컬 저장)</th><th>버전</th>"
             "<th>로컬 재사용</th><th>조직 재사용(events)</th></tr>"
             + "".join(rows) + "</table>") if rows else "<p class='meta'>일치하는 Skill 없음.</p>"
    return "<h2>로컬 저장 Skill</h2>" + search + table


def _render_skill_detail(snapshot: dict, sid: str, ver: str) -> str:
    for s in snapshot.get("skills", []):
        if s["id"] == sid and s["version"] == ver:
            demo = " [DEMO_SEED]" if s.get("demo_seed") else ""
            rows = [
                ("id", s["id"] + demo), ("version", s["version"]), ("digest", s["digest"]),
                ("applicability", s.get("applicability")),
                ("로컬 재사용", s["local_reuse_count"]),
                ("조직 재사용(events)", s["org_reuse_count"]),
            ]
            return "<h2>Skill 상세</h2><table>" + "".join(
                f"<tr><th>{_esc(k)}</th><td>{_esc(v)}</td></tr>" for k, v in rows
            ) + "</table>"
    return "<h2>Skill 상세</h2><p class='meta'>해당 Skill을 찾을 수 없습니다.</p>"


def _render_people(snapshot: dict) -> str:
    rows = [
        f"<tr><td>{_esc(p['alias'])}</td><td>{_esc(p.get('role'))}</td>"
        f"<td>{_esc(p.get('contributions', 0))}</td><td>{_esc(p.get('cross_reuse', 0))}</td></tr>"
        for p in snapshot.get("people", [])
    ]
    table = ("<table><tr><th>alias</th><th>역할</th><th>기여(작성)</th><th>교차 재사용</th></tr>"
             + "".join(rows) + "</table>") if rows else "<p class='meta'>사람 데이터 없음.</p>"
    return "<h2>기여·재사용</h2>" + table


def _render_activity(snapshot: dict) -> str:
    rows = []
    for a in snapshot.get("activity", []):
        ref = a.get("skill_ref", {})
        rows.append(
            f"<tr><td>{_esc(a.get('timestamp') or '-')}</td>"
            f"<td>{_esc(ref.get('id'))}@{_esc(ref.get('version'))}</td>"
            f"<td>{_esc(a.get('reuser_alias'))}</td></tr>"
        )
    table = ("<table><tr><th>시각</th><th>Skill</th><th>재사용자</th></tr>"
             + "".join(rows) + "</table>") if rows else "<p class='meta'>최근 활동 없음.</p>"
    return "<h2>최근 활동</h2>" + table


def render_page(snapshot: dict, path: str, query: dict) -> str:
    """경로+쿼리로 페이지 HTML을 만드는 순수 함수(테스트·서버 공용)."""
    if path == "/":
        return _layout("요약", _render_overview(snapshot), snapshot)
    if path == "/skills":
        q = (query.get("q") or [""])[0]
        return _layout("Skill", _render_skills(snapshot, q), snapshot)
    if path == "/skill":
        sid = (query.get("id") or [""])[0]
        ver = (query.get("version") or [""])[0]
        return _layout("Skill 상세", _render_skill_detail(snapshot, sid, ver), snapshot)
    if path == "/people":
        return _layout("사람", _render_people(snapshot), snapshot)
    if path == "/activity":
        return _layout("활동", _render_activity(snapshot), snapshot)
    raise KeyError(path)  # 정의 외 경로


def _make_handler(snapshot_provider):
    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # 조용한 로그
            pass

        def _reject_write(self):
            # 쓰기·상태변경 메서드는 허용하지 않는다(읽기전용).
            # reason phrase는 latin-1만 허용되므로 ASCII로 둔다.
            self.send_error(405, "Method Not Allowed (read-only dashboard)")

        do_POST = do_PUT = do_DELETE = do_PATCH = _reject_write

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path
            if path not in ALLOWED_PATHS:
                # 정의된 경로만 제공(파일 임의 노출 없음). reason은 ASCII.
                self.send_error(404, "Not Found (defined routes only)")
                return
            try:
                snapshot = snapshot_provider()
                page = render_page(snapshot, path, parse_qs(parsed.query))
            except KeyError:
                self.send_error(404, "Not Found")
                return
            body = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return _Handler


def serve_readonly(snapshot_provider, host: str = "127.0.0.1", port: int = 8765) -> None:
    """localhost 읽기전용 대시보드 서버 기동(Ctrl+C로 종료). 외부 노출·인증 없음."""
    httpd = ThreadingHTTPServer((host, port), _make_handler(snapshot_provider))
    print(f"dashboard: http://{host}:{port}/ (읽기전용, Ctrl+C 종료)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
