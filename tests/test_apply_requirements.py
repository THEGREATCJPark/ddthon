"""P0 user-work acceptance: real pip, retained target environment, truthful counting."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
from hypothesis import given, strategies as st

from skillloop import cli
from skillloop.descriptor import make_descriptor
from skillloop.store import SkillStore
from skillloop.usage import UsageTracker

spec = importlib.util.spec_from_file_location("p0_work_setup", Path(__file__).with_name("prepare_p0_work.py"))
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


@given(st.text(alphabet=" \t", max_size=10), st.text(alphabet="abc 123", max_size=20))
def test_comments_and_whitespace_preserve_requested_target(space, comment):
    text = f"# heading\n{space}skillloop-demo-pkg==1.0.0{space}# {comment}\n"
    assert cli._parse_work_requirements(text) == "skillloop-demo-pkg"


@given(st.sampled_from(["other==1.0.0", "skillloop-demo-pkg==2.0.0", "--index-url example",
                       "-r other.txt", "https://example.invalid/a.whl"]))
def test_unsupported_lines_are_never_discarded(extra):
    with pytest.raises(ValueError, match="UNSUPPORTED_REQUIREMENTS"):
        cli._parse_work_requirements("skillloop-demo-pkg==1.0.0\n" + extra)


def invoke(ctx, run_id="logical-1"):
    return cli.main(["apply-requirements", "--requirements", ctx["requirements"],
                     "--python", ctx["work_python"], "--store", ctx["store"],
                     "--usage", ctx["usage"], "--run-id", run_id])


def count(ctx):
    return UsageTracker(ctx["usage"]).current_count("fix-skillloop-demo-pkg-install", "1.0.0")


def test_real_work_persists_and_counts_exactly_once(tmp_path, monkeypatch, capsys):
    first = setup.prepare_work(tmp_path / "first")
    second = setup.prepare_work(tmp_path / "second")
    # One shared Skill/usage store, two distinct requested work environments.
    second.update(store=first["store"], usage=first["usage"])
    store_before = Path(first["store"]).read_bytes()
    req_before = Path(first["requirements"]).read_bytes()
    def forbidden(*a, **kw):
        pytest.fail("Runtime must not prepare, seed or replace the requested environment")
    for name in ("prepare", "make_clean_venv", "setup_failing", "setup_allow"):
        monkeypatch.setattr(cli.harness, name, forbidden)
    monkeypatch.setattr(cli, "_seed_store", forbidden)
    assert invoke(first) == 0
    assert count(first) == 1
    output = capsys.readouterr().out
    assert "‘python pip 사내환경 적용 방법’ Skill로 설치와 사용 확인을 마쳤습니다." in output
    assert "성공 기록이 1회 추가됐습니다." in output
    assert "팀이 이미 해결한 환경 문제라, 해결법을 다시 탐색하지 않고 처리했습니다." in output
    check = subprocess.run([first["work_python"], "-c",
                            "import skillloop_demo_pkg; import importlib.metadata as m; "
                            "assert m.version('skillloop-demo-pkg') == '1.0.0'"],
                           capture_output=True, text=True)
    assert check.returncode == 0, check.stderr
    assert invoke(first) == 0  # same id, already installed: no forced failure
    assert invoke(first, "new-id-same-installed-work") == 0
    assert count(first) == 1
    repeated = capsys.readouterr().out
    assert "INSTALL_OK_NO_REUSE" in repeated
    assert "성공 기록이 1회 추가" not in repeated
    assert invoke(second, "logical-2") == 0
    assert count(first) == 2
    assert Path(first["work_python"]).is_file()
    assert Path(first["store"]).read_bytes() == store_before
    assert Path(first["requirements"]).read_bytes() == req_before
    events = UsageTracker(first["usage"]).list_shared_events()
    assert len(events) == 2
    assert all(e["skill_ref"]["digest"] == cli.descriptor_mod.compute_digest(cli._DEMO_SKILL_CONTENT)
               for e in events)
    assert str(tmp_path) not in Path(first["usage"]).read_text(encoding="utf-8")


@pytest.fixture
def empty_work(tmp_path):
    return setup.prepare_work(tmp_path / "errors")


@pytest.mark.parametrize("case,expected", [
    ("unsupported", "UNSUPPORTED_REQUIREMENTS"), ("missing-python", "ENV_NOT_READY"),
    ("global-python", "ENV_NOT_READY"), ("missing-store", "STORE_NOT_READY"),
    ("corrupt-store", "ERROR"), ("empty-store", "NO_MATCH"),
    ("bad-digest", "INTEGRITY_ERROR"), ("bad-action", "UNSUPPORTED_PROCEDURE"),
    ("other-content", "CONFIRMATION_REQUIRED"),
])
def test_invalid_request_never_counts(empty_work, capsys, case, expected):
    ctx = empty_work
    if case == "unsupported":
        Path(ctx["requirements"]).write_text("another-package==1\n", encoding="utf-8")
    elif case == "missing-python":
        ctx["work_python"] += ".missing"
    elif case == "global-python":
        ctx["work_python"] = sys._base_executable
    elif case == "missing-store":
        ctx["store"] += ".missing"
    elif case == "corrupt-store":
        Path(ctx["store"]).write_text("{", encoding="utf-8")
    elif case == "empty-store":
        Path(ctx["store"]).write_text('{"skills": {}}', encoding="utf-8")
    else:
        content = copy.deepcopy(cli._DEMO_SKILL_CONTENT)
        if case == "bad-action":
            content["procedure"]["action"] = "file-access"
        if case == "other-content":
            content["origin"]["author"] = "remote"
        d = make_descriptor(content)
        Path(ctx["store"]).write_text('{"skills": {}}', encoding="utf-8")
        SkillStore(ctx["store"]).put(d)
        if case == "bad-digest":
            p = Path(ctx["store"])
            p.write_text(p.read_text(encoding="utf-8").replace(d.digest, "0" * 64), encoding="utf-8")
    assert invoke(ctx) != 0
    assert expected in capsys.readouterr().out
    assert count(ctx) == 0


def test_unrelated_pip_error_is_not_no_match(empty_work, monkeypatch, capsys):
    original = subprocess.run
    def run(args, **kwargs):
        if "-r" in args:
            return subprocess.CompletedProcess(args, 1, "", "ERROR: unexpected pip internal failure")
        return original(args, **kwargs)
    monkeypatch.setattr(cli.subprocess, "run", run)
    assert invoke(empty_work) == 4
    output = capsys.readouterr().out
    assert "INSTALL_ERROR" in output and "NO_MATCH" not in output
    assert count(empty_work) == 0


def test_failed_service_verification_never_counts(empty_work, monkeypatch, capsys):
    def failed(*args):
        return cli.reuse_service.ApplicationResult(1, False, False, False, "allow", False, "logical-1")
    monkeypatch.setattr(cli.reuse_service, "apply_and_verify", failed)
    assert invoke(empty_work) == 6
    output = capsys.readouterr().out
    assert "VERIFICATION_FAILED" in output
    assert "성공 기록이 1회 추가" not in output
    assert count(empty_work) == 0
