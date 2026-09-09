"""U2 ② — replay (C6 ReplayVerifier) 테스트.

검증(U2-V, FR-P1-7 Replay 게이트 입력):
- exact candidate(id/version/digest)를 대상으로 실행하고 candidate_ref로 반환.
- **최초 실행 결과 미재사용**: 상태를 가진 가짜 리더가 호출마다 다른 content를 주도록 하고,
  최초 접근(S1 대역)이 소비한 값이 아니라 Replay가 스스로 새로 접근해 얻은 값으로 판정함을 증명.
- 접근 성공 + read-only 근거(mtime·sha256 무변경, save_called=False) → PASS.
- 실행됐으나 미충족(예: 3개월 미만) → FAIL.
- 환경 미준비(app_open=False) 또는 attach 미가용(method="none") → NOT_RUN(게시 금지).
- Replay PASS ≠ 사람 승인 ≠ 원격 게시(별개 유지) — verdict는 접근 효과만 반영.

Excel/pywin32 미의존: 실제 attach는 _read_via_excel_attach 주입으로 대체(로직 검증).
실제 Excel 통합 실경로는 test_envharness_p1.py::test_real_excel_attach_end_to_end에서 수행.
"""

from __future__ import annotations
from tests.p1_helpers import snapshot, PROC, MAPPING

import pytest

from skillloop import descriptor as desc
from skillloop import envharness_p1 as h
from skillloop import replay as rp
from skillloop.envharness_p1 import EnvContext


_ROWS = [("2026-05", 1200), ("2026-06", 1350), ("2026-07", 1500)]
_PROC = dict(PROC)


def _make_candidate(procedure=None) -> desc.Descriptor:
    content = {
        "id": "skill-file-access-excel",
        "version": "1.0.0",
        "origin": {"unit": "U2", "scenario": "P1"},
        "applicability": {"kind": "file-access", "signals": ["BadZipFile", "office-encrypted"]},
        "procedure": procedure if procedure is not None else dict(_PROC),
    }
    return desc.make_descriptor(content)


def _make_env(tmp_path, app_open=True) -> EnvContext:
    f = tmp_path / "target.xlsx"
    f.write_bytes(h._OLE_CFB_MAGIC + b"\x00" * 100)  # 암호화본 대역(직접 파싱 대상 아님)
    return EnvContext(xlsx_path=str(f), app_open=app_open)


# --- candidate_ref 동일성 + digest 검증 ---

def test_replay_returns_exact_candidate_ref(tmp_path, monkeypatch):
    cand = _make_candidate()
    env = _make_env(tmp_path)
    monkeypatch.setattr(h, "_read_via_excel_attach", lambda e, proc: snapshot(_ROWS))

    res = rp.replay(cand, env)

    assert res.candidate_ref == {"id": cand.id, "version": cand.version, "digest": cand.digest}
    assert res.evidence["candidate_digest_verified"] is True  # 내용→digest 재계산 일치


# --- PASS: 새 접근 성공 + read-only 근거 ---

def test_replay_pass_on_fresh_access_success(tmp_path, monkeypatch):
    cand = _make_candidate()
    env = _make_env(tmp_path)
    monkeypatch.setattr(h, "_read_via_excel_attach", lambda e, proc: snapshot(_ROWS))

    res = rp.replay(cand, env)

    assert res.verdict == rp.PASS
    assert res.evidence["access_ok"] is True
    assert res.evidence["access_method"] == "excel-com-attach"
    # read-only 실측 근거가 접근 실행에서 수집됨(무변경·Save 미호출).
    ae = res.evidence["access_evidence"]
    assert ae["original_unchanged"] is True
    assert ae["save_called"] is False
    assert ae["sha256_before"] == ae["sha256_after"]


def test_replay_uses_candidate_procedure(tmp_path, monkeypatch):
    """candidate.procedure 전달과 대역 접근 결과를 확인한다(실 Excel/시트·열 선택 검증 아님)."""
    cand = _make_candidate()
    env = _make_env(tmp_path)
    seen = {}

    def _reader(e, proc):
        seen["proc"] = proc
        return snapshot(_ROWS)

    monkeypatch.setattr(h, "_read_via_excel_attach", _reader)
    res = rp.replay(cand, env)

    assert seen["proc"] == cand.procedure           # candidate의 procedure를 그대로 실행
    assert res.evidence['access_evidence']['workbook_readable']



# --- ★ 최초 실행 결과 미재사용 검증(핵심) ---

def test_replay_does_not_reuse_first_run_result(tmp_path, monkeypatch):
    """상태를 가진 리더가 호출마다 다른 content를 준다.

    - 최초 접근(S1 대역) = 호출#1 → content A (candidate에 '성공'으로 기록됐다고 가정).
    - Replay는 최초 content를 인자로 받지 않고 스스로 재접근 → 호출#2 → content B.
    - Replay 결과가 A가 아니라 **새로 얻은 B**를 반영해야 한다(재사용 금지 증명).
    """
    call_rows = {
        1: [("2026-06", 1350), ("2026-07", 1500), ("2026-08", 1600)],  # A (최초)
        2: [("2026-07", 1500), ("2026-08", 1600), ("2026-09", 1700)],  # B (재접근)
    }
    counter = {"n": 0}

    def _stateful_reader(e, proc):
        counter["n"] += 1
        return snapshot(call_rows[counter["n"]])

    monkeypatch.setattr(h, "_read_via_excel_attach", _stateful_reader)

    cand = _make_candidate()
    env = _make_env(tmp_path)

    # 최초 접근(S1 대역) — 호출#1 소비. 이 content/verdict를 Replay에 넘기지 않는다.
    first = h.run_file_access_procedure(cand.procedure, env)
    assert first.content == snapshot(call_rows[1])

    # Replay는 최초 결과를 모른 채 스스로 새 접근(호출#2)을 수행한다.
    res = rp.replay(cand, env)

    assert counter["n"] == 2                          # Replay가 실제로 다시 접근함
    assert res.verdict == rp.PASS
    assert res.evidence["reused_first_run_result"] is False
    assert res.evidence["replay_independent"] is True
    # Replay 근거는 최초(A)가 아니라 새로 얻은 B를 반영(행 수 3 동일하지만 값이 다름).
    assert first.content != call_rows[2]
    assert res.evidence["replay_obtained_sheets"] == 1


# --- FAIL: 실행됐으나 접근 효과 미충족 ---

def test_replay_fail_on_insufficient_rows(tmp_path, monkeypatch):
    cand = _make_candidate()
    env = _make_env(tmp_path)
    monkeypatch.setattr(h, "_read_via_excel_attach", lambda e, proc: {'sheets': []})  # 2개월

    res = rp.replay(cand, env)

    assert res.verdict == rp.FAIL
    assert res.evidence["access_ok"] is False
    assert res.evidence["access_evidence"]["workbook_readable"] is False


def test_replay_fail_on_readonly_violation(tmp_path, monkeypatch):
    """읽기 경로가 원본을 변경하면 read-only 위반 → 접근 실패 → FAIL."""
    cand = _make_candidate()
    env = _make_env(tmp_path)

    def _mutating_read(e, proc):
        with open(e.xlsx_path, "ab") as fp:
            fp.write(b"MUT")
        return snapshot(_ROWS)

    monkeypatch.setattr(h, "_read_via_excel_attach", _mutating_read)
    res = rp.replay(cand, env)

    assert res.verdict == rp.FAIL
    assert res.evidence["access_evidence"]["original_unchanged"] is False


# --- NOT_RUN: 환경 미준비 / attach 미가용 ---

def test_replay_not_run_when_app_not_open(tmp_path, monkeypatch):
    cand = _make_candidate()
    env = _make_env(tmp_path, app_open=False)
    # app_open=False면 접근 자체를 시도하지 않아야 한다(리더 호출 금지).
    called = {"n": 0}

    def _reader(e, proc):
        called["n"] += 1
        return snapshot(_ROWS)

    monkeypatch.setattr(h, "_read_via_excel_attach", _reader)
    res = rp.replay(cand, env)

    assert res.verdict == rp.NOT_RUN
    assert called["n"] == 0                     # 미준비 환경에서 접근 시도 안 함
    assert "not ready" in res.evidence["reason"]


def test_replay_not_run_when_attach_unavailable(tmp_path, monkeypatch):
    """app_open=True로 시도했으나 attach 미가용(method='none') → NOT_RUN(FAIL 아님)."""
    cand = _make_candidate()
    env = _make_env(tmp_path, app_open=True)
    monkeypatch.setattr(h, "_read_via_excel_attach", lambda e, proc: None)  # attach 불가

    res = rp.replay(cand, env)

    assert res.verdict == rp.NOT_RUN
    assert res.evidence["access_method"] == "none"


# --- Replay PASS와 승인·게시의 분리(계약 경계) ---

def test_replay_result_has_no_approval_or_publish_flags(tmp_path, monkeypatch):
    """ReplayResult는 접근 효과 verdict만 담고 승인·게시 상태를 만들지 않는다."""
    cand = _make_candidate()
    env = _make_env(tmp_path)
    monkeypatch.setattr(h, "_read_via_excel_attach", lambda e, proc: snapshot(_ROWS))

    res = rp.replay(cand, env)

    assert res.verdict == rp.PASS
    keys = set(res.evidence.keys())
    # 승인/게시 관련 키를 스스로 만들지 않는다(S3가 별도 판정·바인딩).
    assert not (keys & {"approved", "human_approval", "published", "remote", "publish_state"})
