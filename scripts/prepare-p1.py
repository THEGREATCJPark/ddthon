"""Operator-only NASCA(가상) environment preparation; never called by Agent recovery.

Keeps two owned workbooks open. Create STOP in destination to close only these books.
No password, solution or task mapping is written into Agent workspaces.
"""
import argparse
import json
from pathlib import Path
import secrets
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.prepare_p0_work import configure_statusline
from skillloop.cli import _DEMO_SKILL_CONTENT
from skillloop.descriptor import make_descriptor
from skillloop.store import SkillStore


def prepare(destination):
    import win32com.client
    import win32process
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError('New destination required')
    destination.mkdir(parents=True)
    excel = win32com.client.DispatchEx('Excel.Application')
    books = []
    try:
        excel.Visible = True
        excel.DisplayAlerts = False
        profiles = [('cold', 'AAAAA01_직전_3달_생산량.xlsx', '생산현황', 5, 3, 1200),
                    ('warm', 'BBBBB02_직전_3달_생산량.xlsx', '월별실적', 8, 2, 2100)]
        contexts = []
        for name, filename, sheet, row, col, base in profiles:
            work = destination / name; work.mkdir()
            state = work / '.skillloop'; state.mkdir()
            (state / 'context.json').write_text(json.dumps({
                'environment_class': 'internal-managed-document',
                'display_label': '사내환경 · NASCA(가상)', 'virtual': True
            }, ensure_ascii=False, indent=2), encoding='utf-8')
            wb = excel.Workbooks.Add(); books.append(wb)
            ws = wb.Worksheets(1); ws.Name = sheet
            values = [('월', None, None, '생산량')]
            values += [(month, None, None, base + i * 150) for i, month in enumerate(('2026-05', '2026-06', '2026-07'))]
            area = ws.Range(ws.Cells(row, col), ws.Cells(row + 3, col + 3))
            area.NumberFormat = '@'; area.Value2 = tuple(values)
            # Task numeric cells remain numeric, despite month text formatting.
            for i in range(3): ws.Cells(row + i + 1, col + 3).Value2 = base + i * 150
            wb.SaveAs(str(work / filename), FileFormat=51, Password=secrets.token_urlsafe(18))
            store = SkillStore(str(state / 'store.json'))
            store.put(make_descriptor(_DEMO_SKILL_CONTENT))
            (state / 'usage.json').write_text('{"counts":{},"seen_run_ids":[],"events":{}}', encoding='utf-8')
            skilldir = work / '.claude/skills/skillloop'; skilldir.mkdir(parents=True)
            shutil.copyfile(ROOT / '.claude/skills/skillloop/SKILL.md', skilldir / 'SKILL.md')
            ctx = {'product_python': sys.executable, 'work_python': sys.executable,
                   'store': str(state / 'store.json'), 'usage': str(state / 'usage.json'),
                   'environment_context': str(state / 'context.json')}
            (work / 'skillloop-work.json').write_text(json.dumps(ctx, ensure_ascii=False, indent=2), encoding='utf-8')
            configure_statusline(work, ctx)
            contexts.append({'work': str(work), 'xlsx': str(work / filename)})
        (destination / 'ready.json').write_text(json.dumps({'workspaces': contexts,
            'owned_excel_pid': win32process.GetWindowThreadProcessId(excel.Hwnd)[1]}, ensure_ascii=False), encoding='utf-8')
        print('READY: workbooks are open; create STOP file to finish', flush=True)
        deadline = time.monotonic() + 7200
        while time.monotonic() < deadline and not (destination / 'STOP').exists():
            time.sleep(1)
    finally:
        for wb in books:
            try: wb.Close(SaveChanges=False)
            except Exception: pass
        try:
            if excel.Workbooks.Count == 0: excel.Quit()
        except Exception: pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('destination')
    prepare(parser.parse_args().destination)
