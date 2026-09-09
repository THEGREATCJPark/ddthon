"""Operator-only document launcher. Not an Agent recovery path."""
import argparse
import json
from pathlib import Path
import time


def open_document(path):
    import pythoncom
    import win32com.client
    import win32process
    path = Path(path).resolve(strict=True)
    rot = pythoncom.GetRunningObjectTable()
    ctx = pythoncom.CreateBindCtx(0)
    for moniker in rot.EnumRunning():
        try:
            if Path(moniker.GetDisplayName(ctx, None)).resolve() != path:
                continue
            book = win32com.client.Dispatch(rot.GetObject(moniker).QueryInterface(pythoncom.IID_IDispatch))
            if Path(book.FullName).resolve() == path:
                book.Application.Visible = True
                book.Activate()
                return book.Application, book, win32process.GetWindowThreadProcessId(book.Application.Hwnd)[1]
        except Exception:
            continue
    # Use a generated COM wrapper: Excel's optional arguments must be marshalled
    # as missing, not as null positional arguments. Keep this app separately owned.
    excel = win32com.client.gencache.EnsureDispatch(win32com.client.DispatchEx('Excel.Application'))
    excel.Visible = True
    excel.DisplayAlerts = False
    try:
        book = excel.Workbooks.Open(Filename=str(path), UpdateLinks=0, ReadOnly=True,
                                   Password='nowhere', IgnoreReadOnlyRecommended=True,
                                   Notify=False, AddToMru=False)
        if Path(book.FullName).resolve() != path:
            raise RuntimeError('Opened workbook does not match requested path')
        book.Activate()
        excel.Visible = True
        return excel, book, win32process.GetWindowThreadProcessId(excel.Hwnd)[1]
    except BaseException:
        # Only the newly owned application, never a user's existing Excel process.
        for book in list(excel.Workbooks):
            book.Close(SaveChanges=False)
        excel.Quit()
        raise


def main():
    parser = argparse.ArgumentParser(description='문서를 Excel로 열기 (운영자 전용)')
    parser.add_argument('path')
    args = parser.parse_args()
    excel, book, pid = open_document(args.path)
    print('문서가 열렸습니다. Excel에서 내용을 확인하세요.', flush=True)
    print(json.dumps({'excel_pid': pid, 'workbook': book.FullName}), flush=True)
    try:
        while excel.Workbooks.Count:
            time.sleep(1)
    except Exception:
        pass
    # User closes Excel normally. Never Quit an application attached from ROT.


if __name__ == '__main__':
    main()
