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
    with zipfile.ZipFile(str(plain), "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")

    obs = h.attempt_direct_access(str(plain))

    assert obs.ran is True
    assert obs.ok is True
    assert obs.error is None


def test_direct_access_missing_file():
    obs = h.attempt_direct_access("/no/such/file.xlsx")
    assert obs.ran is False and obs.ok is False


# --- 완료월 행 형태 검증(접근 검증 최소 형태) ---

def test_completed_month_rows_shape():
    ok_rows = [("2026-05", 1200), ("2026-06", 1350), ("2026-07", 1500)]
    assert h._looks_like_completed_month_rows(ok_rows) is True
    assert h._looks_like_completed_month_rows(ok_rows[:2]) is False   # 3개 미만
    assert h._looks_like_completed_month_rows([("2026-05", "x")] * 3) is False  # 값 타입
    assert h._looks_like_completed_month_rows([("", 1)] * 3) is False           # 빈 month
    assert h._looks_like_completed_month_rows("nope") is False
    # bool은 int 하위형이지만 총생산량으로 허용하지 않는다.
    assert h._looks_like_completed_month_rows([("2026-05", True)] * 3) is False


# --- run_file_access_procedure: attach 주입으로 read-only·성공기준 검증 ---

_ROWS = [("2026-05", 1200), ("2026-06", 1350), ("2026-07", 1500)]
_PROC = {"action": "read-open-workbook", "sheet": 1, "columns": ["month", "total_output"]}


def _make_env_with_file(tmp_path, app_open=True):
    f = tmp_path / "target.xlsx"
    f.write_bytes(h._OLE_CFB_MAGIC + b"\x00" * 100)  # 암호화본 대역(직접 파싱 대상 아님)
    return h.EnvContext(xlsx_path=str(f), app_open=app_open)


def test_run_procedure_success_readonly(tmp_path, monkeypatch):
    env = _make_env_with_file(tmp_path)
    monkeypatch.setattr(h, "_read_via_excel_attach", lambda e, proc: list(_ROWS))

    res = h.run_file_access_procedure(_PROC, env)

    assert res.ok is True
    assert res.method == "excel-com-attach"
    assert res.content == _ROWS
    assert res.evidence["original_unchanged"] is True
    assert res.evidence["completed_month_rows"] is True
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
    monkeypatch.setattr(h, "_read_via_excel_attach", lambda e, proc: _ROWS[:2])  # 2개월

    res = h.run_file_access_procedure(_PROC, env)

    assert res.ok is False
    assert res.evidence["completed_month_rows"] is False


def test_run_procedure_readonly_gate_catches_modification(tmp_path, monkeypatch):
    """읽기 경로가 원본을 변경하면 mtime/sha256 무변경 기준 위반 → ok=False로 잡힌다."""
    env = _make_env_with_file(tmp_path)

    def _mutating_read(e, proc):
        with open(e.xlsx_path, "ab") as fp:  # 원본 변경(위반 시뮬레이션)
            fp.write(b"MUT")
        return list(_ROWS)

    monkeypatch.setattr(h, "_read_via_excel_attach", _mutating_read)
    res = h.run_file_access_procedure(_PROC, env)

    assert res.ok is False
    assert res.evidence["original_unchanged"] is False


# --- setup/teardown: Excel 미가용 시 정직한 NOT_RUN 경로(연출 없음) ---

def test_setup_without_excel_marks_not_running_and_direct_fails():
    """Excel/pywin32 미가용이면 app_running=False + 비-zip 파일 → 직접 접근 관찰 실패."""
    env = h.setup_encrypted_open_xlsx_env(_ROWS, password="pw-user-only")
    try:
        assert os.path.exists(env.xlsx_path)
        assert env.present_facts["file_state"] == "office-encrypted"
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
        proc = {"action": "read-open-workbook", "sheet": 1,
                "columns": ["month", "total_output"]}
        res = h.run_file_access_procedure(proc, ctx)

        assert res.ok is True
        assert res.method == "excel-com-attach"
        assert res.content == _ROWS
        assert res.evidence["original_unchanged"] is True
        assert res.evidence["save_called"] is False
        assert h._sha256_of(env.xlsx_path) == sha_before
    finally:
        h.teardown()
