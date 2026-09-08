"""C9 연결 — `skillloop match` CLI가 승인된 검색 계약(C5 match.search)을 호출하는지 검증.

소유: CJ. 매칭 로직은 여기서 재구현하지 않으므로 '매핑 규칙' 자체를 검사하지 않는다.
대신 (a) CLI가 실제 store 위에서 검색 계약을 호출해 MATCH/NO_MATCH를 내는지,
(b) 읽기전용(카운트·usage 미생성)인지만 확인한다.
"""

from skillloop import cli
from skillloop.store import SkillStore


def _seed(tmp_path):
    sp = tmp_path / "store.json"
    cli._seed_store(SkillStore(str(sp)))  # 데모 Skill 적재(합성·비민감)
    return str(sp)


def test_match_calls_search_and_reports_match(tmp_path, capsys):
    sp = _seed(tmp_path)
    rc = cli.cmd_match("pip-install-fail:skillloop-demo-pkg",
                       target="skillloop-demo-pkg", store_path=sp)
    out = capsys.readouterr().out
    assert rc == 0
    assert "MATCH" in out
    assert "fix-skillloop-demo-pkg-install" in out


def test_match_no_match_for_unrelated_signal(tmp_path, capsys):
    sp = _seed(tmp_path)
    rc = cli.cmd_match("compile-fail:some-other-thing", store_path=sp)
    out = capsys.readouterr().out
    assert rc == 0
    assert "NO_MATCH" in out


def test_match_is_read_only_no_usage_written(tmp_path):
    sp = _seed(tmp_path)
    cli.cmd_match("pip-install-fail:skillloop-demo-pkg",
                  target="skillloop-demo-pkg", store_path=sp)
    # 읽기전용: match는 usage/counts를 만들지 않는다.
    assert not (tmp_path / "usage.json").exists()
