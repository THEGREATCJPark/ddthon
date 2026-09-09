"""Operator-only mechanical validation on new non-measurement data; no model.

Creates an owned Excel instance and encrypted workbook, then independently reads
the exact workbook through ROT. Closes only its own workbook/empty owned app.
No benchmark input, original workbook, stored key or product registry is used.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_exact_running_workbook(path):
    import pythoncom
    import win32com.client as com
    wanted = os.path.normcase(os.path.abspath(path))
    try:
        app = com.GetActiveObject('Excel.Application')
    except Exception:
        app = None
    if app is not None:
        for book in app.Workbooks:
            if os.path.normcase(os.path.abspath(book.FullName)) == wanted:
                return [[list(row) for row in ws.UsedRange.Value2] for ws in book.Worksheets]
    rot = pythoncom.GetRunningObjectTable()
    context = pythoncom.CreateBindCtx(0)
    for moniker in rot.EnumRunning():
        try:
            name = moniker.GetDisplayName(context, None)
            if os.path.normcase(os.path.abspath(name)) != wanted:
                continue
            book = com.Dispatch(rot.GetObject(moniker).QueryInterface(pythoncom.IID_IDispatch))
            if os.path.normcase(os.path.abspath(book.FullName)) == wanted:
                return [[list(row) for row in ws.UsedRange.Value2] for ws in book.Worksheets]
        except Exception:
            continue
    raise RuntimeError('exact target not discoverable in running Excel')


def main(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    target = root / 'setup-only.xlsx'
    report = {'started_at': datetime.now(timezone.utc).isoformat(),
              'kind': 'MECHANICAL_DERIVED_PROCEDURE_VALIDATION_NOT_AGENT_MEASUREMENT',
              'model_calls': 0, 'measurement_inputs_used': False,
              'injected_skill_sha256': sha(Path(__file__).with_name('p1_comparison_skill.md')),
              'validation_code_sha256': sha(__file__), 'verdict': 'NOT_RUN'}
    app = book = None
    try:
        import pythoncom
        import win32com.client as com
        pythoncom.CoInitialize()
        app = com.DispatchEx('Excel.Application')
        app.Visible = False
        app.DisplayAlerts = False  # only our newly owned setup app
        book = app.Workbooks.Add()
        # Setup data unrelated to the received trial inputs; no answer in Skill.
        expected = [['period', 'quantity'], ['2031-10', 73], ['2031-11', 96], ['2031-12', 89]]
        book.Worksheets(1).Range('C4:D7').Value = tuple(tuple(r) for r in expected)
        password = uuid.uuid4().hex[:12]
        book.SaveAs(str(target), FileFormat=51, Password=password)
        book.Close(SaveChanges=False)
        book = app.Workbooks.Open(str(target), UpdateLinks=0, ReadOnly=True, Password=password)
        password = None
        before, mtime = sha(target), target.stat().st_mtime_ns
        from openpyxl import load_workbook
        try:
            wb = load_workbook(target, read_only=True)
            wb.close()
            direct_failed = False
        except Exception as exc:
            direct_failed = type(exc).__name__ == 'BadZipFile'
            report['direct_exception'] = type(exc).__name__
        # Separate process would be closer to Agent; this check deliberately
        # reports only the mechanically executed read-only recipe.
        actual = read_exact_running_workbook(target)
        checks = {'direct_parser_failed': direct_failed,
                  'actual_values_equal': actual == [expected],
                  'original_unchanged': before == sha(target) and mtime == target.stat().st_mtime_ns,
                  'read_only_open': bool(book.ReadOnly)}
        report.update(checks=checks, excel_version=str(app.Version), excel_build=str(app.Build),
                      input_sha256=before, verdict='PASS' if all(checks.values()) else 'FAIL')
    except Exception as exc:
        report.update(verdict='BLOCKED', error_type=type(exc).__name__, error=str(exc))
    finally:
        if book is not None:
            try: book.Close(SaveChanges=False)
            except Exception: pass
        if app is not None:
            try:
                if app.Workbooks.Count == 0: app.Quit()
            except Exception: pass
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        (root / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    raise SystemExit(main(parser.parse_args().root))
