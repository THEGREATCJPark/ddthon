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


def test_cli_uses_explicit_work_store_from_other_directory(tmp_path, monkeypatch, capsys):
    sp = _seed(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    rc = cli.main(["match", "--signature", "pip-install-fail:skillloop-demo-pkg",
                   "--target", "skillloop-demo-pkg", "--store", sp])
    output = capsys.readouterr().out
    assert rc == 0 and "match: MATCH" in output and "NO_MATCH" not in output


def test_actual_error_input_normalizes_target_and_queries_work_store(tmp_path, capsys):
    sp = _seed(tmp_path)
    err = tmp_path / "pip-stderr.txt"
    err.write_text("ERROR: No matching distribution found for SkillLoop_Demo.Pkg==1.0.0\n",
                   encoding="utf-8")
    assert cli.main(["match", "--pip-stderr", str(err), "--exit-code", "1",
                     "--target", "skillloop-demo-pkg==1.0.0", "--store", sp]) == 0
    output = capsys.readouterr().out
    assert "observation=pip-install-fail:skillloop-demo-pkg" in output
    assert "match: MATCH" in output and "NO_MATCH" not in output
    assert not (tmp_path / "usage.json").exists()


def test_raw_signature_is_rejected_instead_of_false_no_match(tmp_path, capsys):
    assert cli.cmd_match("No matching distribution found for skillloop-demo-pkg==1.0.0",
                         store_path=_seed(tmp_path)) == 2
    output = capsys.readouterr().out
    assert "INVALID_SIGNAL" in output and "NO_MATCH" not in output


def test_observation_requires_explicit_store(tmp_path, capsys):
    assert cli.cmd_match(None, target="other", pip_stderr="missing", exit_code=1) == 2
    assert "STORE_REQUIRED" in capsys.readouterr().out


def test_success_unrelated_or_wrong_target_never_becomes_supply_failure():
    good = "ERROR: No matching distribution found for example-pkg==1.2"
    assert cli._pip_failure_observation("pip install", "example-pkg", 0, good) is None
    assert cli._pip_failure_observation("pip install", "example", 1, good) is None
    assert cli._pip_failure_observation("pip install", "other", 1, good) is None
    assert cli._pip_failure_observation("pip install", "example-pkg", 1, "Permission denied") is None


def test_generic_observation_does_not_encode_known_skill_or_solution():
    obs = cli._pip_failure_observation(
        "pip install", "Another_Package==2.3", 1,
        "ERROR: Could not find a version that satisfies the requirement another-package==2.3 (from versions: none)")
    assert obs.target_pkg == "another-package"
    assert obs.error_signature == "pip-install-fail:another-package"
    assert "skillloop" not in repr(obs) and "allow" not in repr(obs)


def test_unrecognized_observation_reports_not_invoked(tmp_path, capsys):
    sp = _seed(tmp_path)
    err = tmp_path / "error.txt"
    err.write_text("pip internal error", encoding="utf-8")
    assert cli.cmd_match(None, "skillloop-demo-pkg", sp, str(err), 1) == 4
    assert "NOT_INVOKED" in capsys.readouterr().out


def test_observation_normalization_property():
    from hypothesis import given, strategies as st
    @given(st.sampled_from(["Example_Pkg", "example.pkg", "EXAMPLE--PKG"]),
           st.sampled_from(["No matching distribution found for",
                           "Could not find a version that satisfies the requirement"]))
    def check(name, message):
        obs = cli._pip_failure_observation("pip install", "example-pkg==1.0", 1,
                                           f"ERROR: {message} {name}==1.0")
        assert obs.error_signature == "pip-install-fail:example-pkg"
    check()
