"""C7-P1 — EnvHarness(P1): 합성 실패 환경 준비 + 파일접근 procedure 실행 계약.

소유(단일 수정자): B (한석훈)
확정 모델(FD §1, D-5): **Office 암호화 합성 파일 + 실행 중 Excel read-only attach**.
    - 합성 제약 = Excel open password 암호화(FileFormat=51) → 바이트는 OLE-CFB(zip 아님).
    - 직접 접근 = 표준 XLSX 리더(zip 기반)가 암호화본에서 **스스로 BadZipFile**(강제 raise 아님).
    - 허용 대안 = 사용자가 (암호로) 열어둔 실행 중 Excel 인스턴스에 attach(win32com
      GetActiveObject) → 셀 값만 read-only 읽기(Save 미호출·원본 mtime/sha256 무변경).

계약(Code Plan §2, coordination-blockers §C-c):
    - setup_encrypted_open_xlsx_env(data_rows, password) -> XlsxEnv
    - teardown() -> None
    - attempt_direct_access(path) -> DirectAccessObservation   (강제 raise 아님, 관찰만)
    - run_file_access_procedure(procedure, env) -> AccessResult (A/S1·C6 Replay 공용)

경계·정직성:
    - harness는 준비·환경 사실만. 정답 대안(attach)을 Agent에 자동 공급하지 않는다.
    - 평문 암호는 사전조건 소유자(사용자) 것이며 procedure/Agent/후보에 넣지 않는다.
    - Excel/pywin32 미가용 → attach 경로 `ok=False, method="none"`(상위에서 NOT_RUN 매핑).
      결과를 연출하지 않는다(가짜 성공 금지).
    - NFR-RUN-1의 P1 Excel 경로 한정 예외 승인(P0·기타 범위 확대 금지).
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import zipfile
from dataclasses import dataclass, field

# OLE 복합 문서(암호화 Office 컨테이너) 매직 시그니처. OOXML zip(PK\x03\x04)이 아니다.
_OLE_CFB_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

# Excel COM 상수(FileFormat). xlOpenXMLWorkbook = 51.
_XL_OPENXML = 51


@dataclass
class XlsxEnv:
    """harness가 준비한 P1 환경 사실. 정답 대안은 포함하지 않는다."""
    xlsx_path: str
    app_running: bool
    present_facts: dict = field(default_factory=dict)  # {file_state, app_open}


@dataclass
class EnvContext:
    """procedure 실행 대상 환경(harness 준비 사실; 정답 대안 아님)."""
    xlsx_path: str
    app_open: bool


@dataclass
class DirectAccessObservation:
    """표준 zip 리더를 실제 실행하고 관찰한 결과(강제 raise 아님)."""
    ran: bool
    ok: bool
    error: str | None
    evidence: dict = field(default_factory=dict)


@dataclass
class AccessResult:
    """파일접근 procedure 실행 결과. ok는 실제 효과 기반(강제 raise로 연출 금지)."""
    ok: bool
    content: list | None          # [(month:str, total_output:int|float), ...] | None
    method: str                   # "excel-com-attach" | "direct-zip" | "none"
    evidence: dict = field(default_factory=dict)


# --- 내부 유틸(순수, Excel 미의존 → 테스트 가능) ---

def _sha256_of(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _mtime_of(path: str) -> float | None:
    return os.path.getmtime(path) if os.path.exists(path) else None


def _looks_like_completed_month_rows(content) -> bool:
    """content가 3개 완료월 (month, total_output) 행을 포함하는지(접근 성공 기준 2).

    업무 입력 검증(S2, month/total_output 값의 업무적 타당성)과는 구분되는
    **접근 검증 최소 형태 확인**만 수행한다(형태·개수).
    """
    if not isinstance(content, (list, tuple)) or len(content) < 3:
        return False
    for row in content:
        if not (isinstance(row, (list, tuple)) and len(row) == 2):
            return False
        month, total = row
        if not isinstance(month, str) or not month.strip():
            return False
        if not isinstance(total, (int, float)) or isinstance(total, bool):
            return False
    return True


# --- COM(Excel) 경계: 미가용 시 정직하게 실패 반환(연출 금지) ---

def _write_encrypted_placeholder(path: str) -> None:
    """Excel/pywin32 미가용 시, 직접 접근 관찰용 **비-zip(OLE-CFB) 컨테이너 형태** 파일 기록.

    실제 Office 암호화가 아니라 '표준 zip 리더가 자연히 BadZipFile을 내는 비-zip 바이트'로,
    FR-P1-1의 직접 접근 실패 관찰(강제 raise 아님)만 재현한다. attach 대안은 Excel 실경로
    필요 → 이 경우 app_running=False로 두어 상위에서 NOT_RUN 처리한다.
    """
    with open(path, "wb") as f:
        f.write(_OLE_CFB_MAGIC)
        f.write(b"\x00" * 504)  # CFB 헤더 크기(512B) 근사 패딩. zip 아님.


# 실행 중 Excel 인스턴스 참조를 모듈에 유지(사용자가 열어둔 상태 대역).
# 로컬 변수로 두면 함수 반환 시 COM 참조가 GC되어 Excel이 종료 → GetActiveObject 실패.
_excel_app = None


def _try_com_create_encrypted(data_rows, password: str, path: str) -> bool:
    """win32com로 실제 Office 암호화본 생성 + 열어둔 상태 준비. 미가용이면 False.

    성공(True)이면 실행 중 Excel 인스턴스에 워크북이 열려 있다(사용자 열람 상태 대역).
    앱 참조는 모듈에 유지해 인스턴스가 살아 있게 하고, Visible=True로 ROT에 등록해
    이후 GetActiveObject(attach)가 발견할 수 있게 한다. 실패/미가용이면 False(연출 없음).
    """
    global _excel_app
    try:
        import win32com.client  # type: ignore
    except Exception:
        return False
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = True          # ROT 등록(GetActiveObject 발견 가능)
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Add()
        ws = wb.Worksheets(1)
        for i, (month, total) in enumerate(data_rows, start=1):
            ws.Cells(i, 1).Value = month
            ws.Cells(i, 2).Value = total
        # open password로 암호화 저장(FileFormat=51). Password는 사전조건 소유자 것.
        wb.SaveAs(path, FileFormat=_XL_OPENXML, Password=password)
        wb.Close(SaveChanges=False)
        # 사용자가 (암호로) 열어둔 상태 대역: 암호로 다시 연다.
        excel.Workbooks.Open(path, Password=password)
        _excel_app = excel            # 인스턴스 유지(함수 반환 후 종료 방지)
        return True
    except Exception:
        return False


# 테스트 주입 지점: 실제 Excel attach 대신 monkeypatch 가능(Excel 미가용 시 read-only 로직 검증용).
def _read_via_excel_attach(env: EnvContext):
    """실행 중 Excel 인스턴스에 attach → 셀 값 read-only 읽기. 미가용이면 None.

    반환: content=[(month, total_output), ...] 또는 None(attach/읽기 불가).
    **Save 계열을 호출하지 않는다**(read-only). 원본 파일 바이트를 직접 열지 않고,
    애플리케이션이 이미 복호화한 문서를 매개로 값만 읽는다.
    """
    if not env.app_open:
        return None
    try:
        import win32com.client  # type: ignore
    except Exception:
        return None
    try:
        excel = win32com.client.GetActiveObject("Excel.Application")
    except Exception:
        return None
    try:
        target = os.path.normcase(os.path.abspath(env.xlsx_path))
        for wb in excel.Workbooks:
            if os.path.normcase(os.path.abspath(wb.FullName)) != target:
                continue
            ws = wb.Worksheets(1)
            used = ws.UsedRange
            rows = []
            for r in range(1, used.Rows.Count + 1):
                month = ws.Cells(r, 1).Value
                total = ws.Cells(r, 2).Value
                if month is None:
                    continue
                # COM은 정수도 float로 줄 수 있음 → 정수형은 int로 정규화(값 보존).
                if isinstance(total, float) and total.is_integer():
                    total = int(total)
                rows.append((str(month), total))
            return rows  # Save 미호출: 읽기만 하고 반환.
        return None
    except Exception:
        return None


# --- 공개 계약 ---

_active: XlsxEnv | None = None


def setup_encrypted_open_xlsx_env(data_rows, password: str) -> XlsxEnv:
    """정상 데이터를 Office 암호화 저장 + 사용자 열람(실행 중 Excel) 상태를 준비만 한다.

    정답 대안(attach)은 공급하지 않는다. password는 사전조건 소유자(사용자) 것이며
    Agent/후보 절차에 넘기지 않는다(여기서만 생성에 사용).
    Excel/pywin32 미가용 → 직접 접근 관찰용 비-zip 파일만 기록하고 app_running=False
    (상위에서 attach 경로를 NOT_RUN 처리).
    """
    global _active
    fd, path = tempfile.mkstemp(prefix="skillloop_p1_", suffix=".xlsx")
    os.close(fd)
    os.remove(path)  # COM SaveAs가 새로 쓰도록 빈 경로만 확보.

    app_running = _try_com_create_encrypted(data_rows, password, path)
    if not app_running:
        _write_encrypted_placeholder(path)  # 직접 접근 실패 관찰 재현(비-zip)

    _active = XlsxEnv(
        xlsx_path=path,
        app_running=app_running,
        present_facts={"file_state": "office-encrypted", "app_open": app_running},
    )
    return _active


def teardown() -> None:
    """열어둔 Excel/워크북 정리 + 원본 파일 제거. 원본 미변경 전제(read-only)."""
    global _active, _excel_app
    if _excel_app is not None:
        try:
            _excel_app.DisplayAlerts = False
            for wb in list(_excel_app.Workbooks):
                wb.Close(SaveChanges=False)   # read-only: 저장 없이 닫기
            _excel_app.Quit()
        except Exception:
            pass
        _excel_app = None
    if _active is not None:
        try:
            if os.path.exists(_active.xlsx_path):
                os.remove(_active.xlsx_path)
        except OSError:
            pass
        _active = None


def attempt_direct_access(path: str) -> DirectAccessObservation:
    """표준 XLSX 리더(zip 기반)를 실제 실행하고 결과만 관찰(대안 미제시).

    암호화본은 zip이 아니므로 리더가 **스스로 BadZipFile**을 낸다(잘못된 API·강제 raise 아님).
    평문 OOXML이면 정상 open → ok=True(대조군). 여기서는 예외를 잡아 관찰로 변환할 뿐이다.
    """
    if not os.path.exists(path):
        return DirectAccessObservation(
            ran=False, ok=False, error="file not found",
            evidence={"path": path},
        )
    try:
        with zipfile.ZipFile(path) as zf:  # 표준 리더의 근간(openpyxl/pandas도 zip 전제)
            names = zf.namelist()
        return DirectAccessObservation(
            ran=True, ok=True, error=None,
            evidence={"reader": "zipfile", "entries": len(names)},
        )
    except zipfile.BadZipFile as exc:
        return DirectAccessObservation(
            ran=True, ok=False, error=f"BadZipFile: {exc}",
            evidence={"reader": "zipfile", "reason": "not a zip (office-encrypted)"},
        )
    except Exception as exc:  # 기타 리더 오류도 관찰로 반환(강제 raise 아님)
        return DirectAccessObservation(
            ran=True, ok=False, error=f"{type(exc).__name__}: {exc}",
            evidence={"reader": "zipfile"},
        )


def run_file_access_procedure(procedure: dict, env: EnvContext) -> AccessResult:
    """후보 procedure를 대상 env에 실제 실행하고 접근 효과·read-only 증거로 판정.

    접근 성공(ok=True) 기준(FD §1, coordination-blockers §C-c):
      (1) 원본 바이트 직접 파싱 아님·허용 경로(실행 중 Excel attach)로 content 획득,
      (2) content가 3개 완료월 (month, total_output) 행 포함,
      (3) 원본 mtime·sha256 무변경 & Save 계열 미호출(read-only 증거).
    미충족/실패 → ok=False(강제 raise 아님). Excel 미열림/미가용 → method="none".

    A(S1 파일접근 분기)와 C6 Replay가 동일 계약으로 호출한다. procedure는 서술적 접근
    절차만 담으며(스크립트·업무 계산·평문 암호 미포함) 여기서 실행 대상 사실로 참조된다.
    """
    sha_before = _sha256_of(env.xlsx_path)
    mtime_before = _mtime_of(env.xlsx_path)
    evidence: dict = {
        "procedure_keys": sorted(procedure.keys()) if isinstance(procedure, dict) else None,
        "app_open": env.app_open,
        "sha256_before": sha_before,
        "mtime_before": mtime_before,
        "save_called": False,   # attach 읽기 경로는 Save를 호출하지 않는다.
    }

    content = _read_via_excel_attach(env)
    if content is None:
        evidence["error"] = "excel attach unavailable or not open"
        return AccessResult(ok=False, content=None, method="none", evidence=evidence)

    sha_after = _sha256_of(env.xlsx_path)
    mtime_after = _mtime_of(env.xlsx_path)
    evidence["sha256_after"] = sha_after
    evidence["mtime_after"] = mtime_after

    unchanged = (sha_before == sha_after) and (mtime_before == mtime_after)
    has_rows = _looks_like_completed_month_rows(content)
    evidence["original_unchanged"] = unchanged
    evidence["completed_month_rows"] = has_rows

    ok = bool(content is not None and has_rows and unchanged and not evidence["save_called"])
    return AccessResult(
        ok=ok,
        content=content if ok else None,
        method="excel-com-attach",
        evidence=evidence,
    )
