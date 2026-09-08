"""U2 ① — envharness_p1 (C7-P1) 테스트.

검증(U2-V1 일부):
- 직접 접근이 암호화(비-zip) 본에서 **실제 실행 관찰 실패**(BadZipFile, 강제 raise 아님).
- 평문 zip 대조군은 직접 접근 성공(⇒ 실패 원인=환경, API 아님).
- run_file_access_procedure의 접근 성공 3기준(원본 미파싱·3개월 행·mtime/sha256 무변경&Save 미호출).
- Excel 미열림/미가용 → method="none", ok=False(상위 NOT_RUN 매핑).
- read-only 게이트: 읽기 중 원본이 변경되면 ok=False로 잡힌다.

Excel/pywin32 미가용 환경에서도 실행되도록 실제 attach는 _read_via_excel_attach 주입으로 대체.
실제 Excel 통합(attach 실경로)은 Excel 있을 때만 수행 → 그 외 NOT_RUN.
"""

from __future__ import annotations
from tests.p1_helpers import snapshot, PROC, MAPPING

import os
import zipfile

import pytest

from skillloop import envharness_p1 as h


# --- attempt_direct_access: 암호화(비-zip) 실패 관찰 + 평문 대조군 성공 ---

def test_direct_access_on_encrypted_placeholder_observes_badzip(tmp_path):
    enc = tmp_path / "encrypted.xlsx"
    h._write_encrypted_placeholder(str(enc))  # OLE-CFB 매직(비-zip)

    obs = h.attempt_direct_access(str(enc))

    assert obs.ran is True
    assert obs.ok is False               # 리더가 스스로 실패(강제 raise 아님)
    assert "BadZipFile" in (obs.error or "")


def test_direct_access_on_plain_zip_succeeds_control(tmp_path):
    # 평문 OOXML 대조군(최소 zip). 동일 리더가 성공 ⇒ 실패 원인은 환경(암호화)이지 API 아님.
    plain = tmp_path / "plain.xlsx"
    from openpyxl import Workbook
    book = Workbook(); book.active.append(['month', 'output']); book.save(plain); book.close()

    obs = h.attempt_direct_access(str(plain))

    assert obs.ran is True
    assert obs.ok is True
    assert obs.error is None


def test_direct_access_missing_file():
    obs = h.attempt_direct_access("/no/such/file.xlsx")
    assert obs.ran is False and obs.ok is False


# --- 완료월 행 형태 검증(접근 검증 최소 형태) ---

def test_workbook_readable_shape():
    assert h._valid_snapshot(snapshot([['any text']]))
    assert h._valid_snapshot(snapshot([[None, True]]))  # capability is not a numeric task
    assert not h._valid_snapshot({'sheets': []})
    assert not h._valid_snapshot(snapshot([]))
    assert not h._valid_snapshot(snapshot([[1], [1, 2]]))


# --- run_file_access_procedure: attach 주입으로 read-only·성공기준 검증 ---

_ROWS = [("2026-05", 1200), ("2026-06", 1350), ("2026-07", 1500)]
_PROC = dict(PROC)


def _make_env_with_file(tmp_path, app_open=True):
    f = tmp_path / "target.xlsx"
    f.write_bytes(h._OLE_CFB_MAGIC + b"\x00" * 100)  # 암호화본 대역(직접 파싱 대상 아님)
    return h.EnvContext(xlsx_path=str(f), app_open=app_open)


def test_run_procedure_success_readonly(tmp_path, monkeypatch):
    env = _make_env_with_file(tmp_path)
    monkeypatch.setattr(h, "_read_via_excel_attach", lambda e, proc: snapshot(_ROWS))

    res = h.run_file_access_procedure(_PROC, env)

    assert res.ok is True
    assert res.method == "excel-com-attach"
    assert res.content['sheets'][0]['values'] == [list(r) for r in _ROWS]
    assert res.evidence["original_unchanged"] is True
    assert res.evidence["workbook_readable"] is True
    assert res.evidence["save_called"] is False
    assert res.evidence["sha256_before"] == res.evidence["sha256_after"]


def test_run_procedure_app_not_open_is_none(tmp_path, monkeypatch):
    env = _make_env_with_file(tmp_path, app_open=False)
    # app_open=False면 주입 리더까지 가지 않고 None 처리되어야 한다(실제 함수는 app_open 가드).
    monkeypatch.setattr(h, "_read_via_excel_attach", lambda e, proc: None)

    res = h.run_file_access_procedure(_PROC, env)

    assert res.ok is False
    assert res.method == "none"
    assert res.content is None


def test_run_procedure_insufficient_rows(tmp_path, monkeypatch):
    env = _make_env_with_file(tmp_path)
    monkeypatch.setattr(h, "_read_via_excel_attach", lambda e, proc: {'sheets': []})  # 2개월

    res = h.run_file_access_procedure(_PROC, env)

    assert res.ok is False
    assert res.evidence["workbook_readable"] is False


def test_run_procedure_readonly_gate_catches_modification(tmp_path, monkeypatch):
    """읽기 경로가 원본을 변경하면 mtime/sha256 무변경 기준 위반 → ok=False로 잡힌다."""
    env = _make_env_with_file(tmp_path)

    def _mutating_read(e, proc):
        with open(e.xlsx_path, "ab") as fp:  # 원본 변경(위반 시뮬레이션)
            fp.write(b"MUT")
        return snapshot(_ROWS)

    monkeypatch.setattr(h, "_read_via_excel_attach", _mutating_read)
    res = h.run_file_access_procedure(_PROC, env)

    assert res.ok is False
    assert res.evidence["original_unchanged"] is False


# --- setup/teardown: Excel 미가용 시 정직한 NOT_RUN 경로(연출 없음) ---

def test_setup_without_excel_marks_not_running_and_direct_fails(monkeypatch):
    """Excel/pywin32 미가용이면 app_running=False + 비-zip 파일 → 직접 접근 관찰 실패."""
    monkeypatch.setattr(h, "_try_com_create_encrypted", lambda *a: False)
    env = h.setup_encrypted_open_xlsx_env(_ROWS, password="pw-user-only")
    try:
        assert os.path.exists(env.xlsx_path)
        assert env.present_facts["file_state"] == "non-office-placeholder"
        # Excel 있으면 app_running=True(실경로), 없으면 False. 어느 쪽이든 직접 접근은 실패해야 한다.
        obs = h.attempt_direct_access(env.xlsx_path)
        assert obs.ran is True
        assert obs.ok is False  # 암호화본은 zip이 아니다.
        # app_running과 present_facts.app_open 정합.
        assert env.present_facts["app_open"] == env.app_running
    finally:
        h.teardown()
    # teardown은 모듈 상태를 리셋한다(파일 삭제는 best-effort — Excel이 잠깐 락을 쥘 수 있음).
    assert h._active is None
    assert h._excel_app is None


# --- 실제 Excel 통합(있을 때 PASS, 없으면 NOT_RUN=skip) ---

@pytest.mark.skipif(os.environ.get('SKILLLOOP_RUN_EXCEL_TESTS') != '1',
                    reason='Interactive Excel integration requires explicit SKILLLOOP_RUN_EXCEL_TESTS=1; see recorded real timeout')
def test_real_excel_attach_end_to_end():
    """실 Excel 있을 때: 암호화 직접접근 실패 관찰 + 실제 attach 읽기·원본 무변경(U2-V1).

    Excel/pywin32 미가용(app_running=False) → NOT_RUN(skip). 강제 통과·연출 없음.
    """
    env = h.setup_encrypted_open_xlsx_env(_ROWS, password="pw-user-only")
    try:
        if not env.app_running:
            pytest.skip("Excel/pywin32 미가용 → P1 attach 경로 NOT_RUN")

        # (1) 직접 접근은 암호화본에서 실제 실패해야 한다.
        obs = h.attempt_direct_access(env.xlsx_path)
        assert obs.ran is True and obs.ok is False
        assert "BadZipFile" in (obs.error or "")

        # (2) 실제 attach 읽기(주입 없음) — 원본과 일치·무변경·Save 미호출.
        sha_before = h._sha256_of(env.xlsx_path)
        ctx = h.EnvContext(xlsx_path=env.xlsx_path, app_open=env.app_running)
        proc = dict(PROC)
        res = h.run_file_access_procedure(proc, ctx)

        assert res.ok is True
        assert res.method == "excel-com-attach"
        assert res.content['sheets'][0]['values'] == [list(r) for r in _ROWS]
        assert res.evidence["original_unchanged"] is True
        assert res.evidence["save_called"] is False
        assert h._sha256_of(env.xlsx_path) == sha_before
    finally:
        h.teardown()
