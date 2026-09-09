"""Operator-only NASCA(가상) environment preparation; never called by Agent recovery.

Keeps two owned workbooks open. Create STOP in destination to close only these books.
No password, solution or task mapping is written into Agent workspaces.
"""
import argparse
import getpass
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


def validate_operator_password(password):
    if not password:
        raise ValueError('Empty password is not allowed')
    if len(password) > 15:
        raise ValueError('Excel SaveAs supports at most 15 password characters')
    return password


def read_operator_password():
    if not sys.stdin.isatty():
        raise RuntimeError('--ask-password requires an interactive terminal; do not pipe a password')
    password = validate_operator_password(getpass.getpass(
        '운영자용 파일 암호 (1~15자, 입력 숨김, Agent에게 전달하지 마세요): '))
    if password != getpass.getpass('암호 다시 입력: '):
        raise ValueError('Passwords do not match')
    return password


def prepare(destination, *, operator_password=None):
    if operator_password is not None:
        validate_operator_password(operator_password)
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
            wb.SaveAs(str(work / filename), FileFormat=51,
                      Password=operator_password if operator_password is not None else secrets.token_urlsafe(10))
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
        books[0].Activate()
        excel.Visible = True
        print('READY: workbooks are open; create STOP file to finish', flush=True)
        print('Cold 문서는 이미 열린 Excel 창에서 확인하세요. 이 터미널은 유지하세요.', flush=True)
        if operator_password is not None:
            print('파일을 다시 열 때는 방금 정한 운영자 암호를 직접 입력하세요. Agent에게 전달하지 마세요.', flush=True)
        else:
            print('임의 암호는 보관하지 않습니다. 다시 열 수 있어야 한다면 새 폴더에 --ask-password로 준비하세요.', flush=True)
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
    parser = argparse.ArgumentParser(description='운영자 전용 P1 환경 준비: 이미 열린 Excel을 유지합니다.')
    parser.add_argument('destination')
    parser.add_argument('--ask-password', action='store_true',
                        help='운영자가 재열람할 암호를 숨김 입력합니다. 암호를 인자·파일·로그에 기록하지 않습니다.')
    args = parser.parse_args()
    prepare(args.destination, operator_password=read_operator_password() if args.ask_password else None)
