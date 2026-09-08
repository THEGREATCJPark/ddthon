"""Operator-only P0 work fixture preparation; never called by the product workflow.

Usage (from checkout with declared development dependencies installed):
python tests/prepare_p0_work.py <new-work-directory>
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skillloop import envharness_p0 as harness
from skillloop.cli import _DEMO_SKILL_CONTENT
from skillloop.descriptor import make_descriptor
from skillloop.store import SkillStore


def configure_statusline(project: Path, context: dict) -> dict:
    """Merge a project-local command; never read or modify global Claude settings."""
    settings_path = project / ".claude/settings.local.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.is_file() else {}
    argv = [Path(context["product_python"]).as_posix(), "-m", "skillloop", "status",
            "--store", Path(context["store"]).as_posix(),
            "--usage", Path(context["usage"]).as_posix()]
    settings["statusLine"] = {"type": "command", "command": shlex.join(argv)}
    settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    return settings["statusLine"]


def prepare_work(destination: Path) -> dict:
    destination = destination.resolve()
    if destination.exists():
        raise ValueError("Use a new work directory; existing work is never overwritten")
    harness.prepare()
    destination.mkdir(parents=True)
    venv = destination / ".venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True,
                   capture_output=True, text=True)
    py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    # Site-local pip configuration persists for both normal Agent pip and product calls.
    config_name = "pip.ini" if os.name == "nt" else "pip.conf"
    (venv / config_name).write_text(
        "[global]\nno-index = true\nno-cache-dir = true\ndisable-pip-version-check = true\n"
        f"find-links = {harness.resolve_index('failing')}\n", encoding="utf-8")
    absent = subprocess.run([str(py), "-m", "pip", "show", harness.TARGET_PKG],
                            capture_output=True, text=True)
    if absent.returncode == 0:
        raise RuntimeError("Fresh work environment unexpectedly contains the requested package")
    shutil.copyfile(ROOT / "tests/fixtures/work/requirements.txt", destination / "requirements.txt")
    state = destination / ".skillloop"
    state.mkdir()
    store = SkillStore(str(state / "store.json"))
    store.put(make_descriptor(_DEMO_SKILL_CONTENT))
    unrelated = copy.deepcopy(_DEMO_SKILL_CONTENT)
    unrelated.update(id="unrelated-compile", applicability={"signals": ["compile-fail:unrelated"]})
    store.put(make_descriptor(unrelated))
    (state / "usage.json").write_text(
        json.dumps({"counts": {}, "seen_run_ids": [], "events": {}}), encoding="utf-8")
    skills = destination / ".claude/skills/skillloop"
    skills.mkdir(parents=True)
    shutil.copyfile(ROOT / ".claude/skills/skillloop/SKILL.md", skills / "SKILL.md")
    context = {
        "product_python": sys.executable,
        "work_python": str(py),
        "requirements": str(destination / "requirements.txt"),
        "store": str(state / "store.json"),
        "usage": str(state / "usage.json"),
        "scope": "synthetic P0 work project; existing local Skills preapproved by operator",
    }
    (destination / "skillloop-work.json").write_text(
        json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
    configure_statusline(destination, context)
    return context


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare_work(args.destination), ensure_ascii=False, indent=2))
