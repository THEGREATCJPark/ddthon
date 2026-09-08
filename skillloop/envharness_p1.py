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
import math
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
    content: dict | None          # local workbook snapshot; never shared task data
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
_excel_book = None


def _try_com_create_encrypted(data_rows, password: str, path: str) -> bool:
    """win32com로 실제 Office 암호화본 생성 + 열어둔 상태 준비. 미가용이면 False.

    성공(True)이면 실행 중 Excel 인스턴스에 워크북이 열려 있다(사용자 열람 상태 대역).
    앱 참조는 모듈에 유지해 인스턴스가 살아 있게 하고, Visible=True로 ROT에 등록해
    이후 GetActiveObject(attach)가 발견할 수 있게 한다. 실패/미가용이면 False(연출 없음).
    """
    global _excel_app, _excel_book
    try:
        import win32com.client  # type: ignore
    except Exception:
        return False
    try:
        excel = win32com.client.DispatchEx("Excel.Application")
        _excel_app = excel  # only this newly owned instance may be cleaned up
        excel.Visible = False          # ROT 등록(GetActiveObject 발견 가능)
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Add()
        _excel_book = wb
        ws = wb.Worksheets(1)
        for i, (month, total) in enumerate(data_rows, start=1):
            ws.Cells(i, 1).Value = month
            ws.Cells(i, 2).Value = total
        # open password로 암호화 저장(FileFormat=51). Password는 사전조건 소유자 것.
        wb.SaveAs(path, FileFormat=_XL_OPENXML, Password=password)
        # SaveAs leaves the authorized document open; reopening caused a real COM timeout.
        _excel_book = wb
        _excel_app = excel            # 인스턴스 유지(함수 반환 후 종료 방지)
        return True
    except Exception:
        teardown()
        return False


class AccessUnavailable(RuntimeError):
    """Precondition unavailable, distinct from a running reader failure."""


def _cell_value(value):
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("nonfinite Excel value")
        return int(value) if value.is_integer() else value
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)


def _snapshot_workbook(wb):
    """Read used cell ranges; no production schema or task column selection."""
    sheets = []
    for ws in wb.Worksheets:
        used = ws.UsedRange
        first_row, first_col = int(used.Row), int(used.Column)
        nrows, ncols = int(used.Rows.Count), int(used.Columns.Count)
        raw = used.Value2
        if nrows == ncols == 1:
            raw = ((raw,),)
        values = [[_cell_value(v) for v in row] for row in raw]
        sheets.append({'name': str(ws.Name), 'first_row': first_row,
                       'first_col': first_col, 'values': values})
    return {'sheets': sheets}


def _valid_snapshot(content):
    if not isinstance(content, dict) or not isinstance(content.get('sheets'), list):
        return False
    for sheet in content['sheets']:
        if (not isinstance(sheet, dict) or not isinstance(sheet.get('name'), str)
            or type(sheet.get('first_row')) is not int or sheet['first_row'] < 1
            or type(sheet.get('first_col')) is not int or sheet['first_col'] < 1):
            return False
        rows = sheet.get('values')
        if not isinstance(rows, list) or not rows or not all(isinstance(r, list) for r in rows):
            return False
        if not rows[0] or any(len(r) != len(rows[0]) for r in rows):
            return False
    return bool(content['sheets'])


def _read_via_excel_attach(env: EnvContext, procedure: dict):
    """Attach to an already open workbook. Never opens/decrypts/saves it."""
    if not env.app_open:
        raise AccessUnavailable('environment: workbook not reported open')
    try:
        import win32com.client
    except ImportError as exc:
        raise AccessUnavailable('dependency: pywin32 unavailable') from exc
    try:
        excel = _excel_app if _excel_app is not None else win32com.client.GetActiveObject('Excel.Application')
    except Exception as exc:
        raise AccessUnavailable('attach: running Excel unavailable') from exc
    # Errors after attachment are real failed execution, not NOT_RUN.
    target = os.path.normcase(os.path.abspath(env.xlsx_path))
    for wb in excel.Workbooks:
        if os.path.normcase(os.path.abspath(wb.FullName)) == target:
            return _snapshot_workbook(wb)
    raise AccessUnavailable('workbook: target is not open in attached Excel')


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
        present_facts={"file_state": "office-encrypted" if app_running else "non-office-placeholder", "app_open": app_running},
    )
    return _active


def teardown() -> None:
    """열어둔 Excel/워크북 정리 + 원본 파일 제거. 원본 미변경 전제(read-only)."""
    global _active, _excel_app, _excel_book
    if _excel_app is not None:
        try:
            _excel_app.DisplayAlerts = False
            if _excel_book is not None:
                _excel_book.Close(SaveChanges=False)
            if _excel_app.Workbooks.Count == 0:
                _excel_app.Quit()
        except Exception:
            pass
        _excel_app = None
        _excel_book = None
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
        from openpyxl import load_workbook
    except ImportError:
        return DirectAccessObservation(False, False, 'openpyxl dependency unavailable', {'reader': 'openpyxl'})
    try:
        book = load_workbook(path, read_only=True, data_only=True)
        try:
            names = book.sheetnames
        finally:
            book.close()
        return DirectAccessObservation(True, True, None, {'reader': 'openpyxl', 'sheets': len(names)})
    except Exception as exc:
        return DirectAccessObservation(True, False, f'{type(exc).__name__}: {exc}', {'reader': 'openpyxl'})


def run_file_access_procedure(procedure: dict, env: EnvContext) -> AccessResult:
    """Execute environment capability only; task mapping and data stay local."""
    if procedure != {'action': 'file-access', 'method': 'excel-com-attach'}:
        return AccessResult(False, None, 'invalid-procedure', {'ran': False, 'error': 'unsupported environment procedure'})
    if not env.app_open:
        return AccessResult(False, None, 'none', {'ran': False, 'stage': 'environment', 'error': 'workbook not reported open'})
    evidence = {'sha256_before': _sha256_of(env.xlsx_path), 'mtime_before': _mtime_of(env.xlsx_path),
                'save_called': False, 'ran': False, 'stage': 'attach', 'app_open': env.app_open}
    try:
        content = _read_via_excel_attach(env, procedure)
        if content is None:
            raise AccessUnavailable('attach: no running workbook')
    except AccessUnavailable as exc:
        evidence['error'] = str(exc)
        return AccessResult(False, None, 'none', evidence)
    except Exception as exc:
        evidence.update(ran=True, stage='workbook-read', error=f'{type(exc).__name__}: {exc}')
        return AccessResult(False, None, 'excel-com-attach', evidence)
    evidence.update(ran=True, stage='read-complete', sha256_after=_sha256_of(env.xlsx_path),
                    mtime_after=_mtime_of(env.xlsx_path))
    unchanged = (bool(evidence['sha256_before']) and evidence['sha256_before'] == evidence['sha256_after']
                 and evidence['mtime_before'] is not None and evidence['mtime_before'] == evidence['mtime_after'])
    evidence['original_unchanged'] = unchanged
    evidence['workbook_readable'] = _valid_snapshot(content)
    ok = unchanged and evidence['workbook_readable']
    return AccessResult(bool(ok), content if ok else None, 'excel-com-attach', evidence)
