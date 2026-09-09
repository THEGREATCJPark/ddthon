import importlib.util, json, tempfile, hashlib, sys
from pathlib import Path
import win32com.client
from openpyxl import load_workbook
out=Path('result/operator-org-cold-20260909')
work=Path(tempfile.mkdtemp(prefix='skillloop-operator-open-'))
spec=importlib.util.spec_from_file_location('opener',Path('scripts/open-p1-document.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
for i in range(2):
    path=work/f'document-{i}.xlsx'
    app=win32com.client.gencache.EnsureDispatch(win32com.client.DispatchEx('Excel.Application'))
    app.Visible=False;app.DisplayAlerts=False
    book=app.Workbooks.Add();book.Worksheets(1).Cells(3+i,2+i).Value2=121+i
    book.SaveAs(Filename=str(path),FileFormat=51,Password='nowhere')
    book.Close(SaveChanges=False);app.Quit()
    before=hashlib.sha256(path.read_bytes()).hexdigest()
    try: load_workbook(path);direct='UNEXPECTED_SUCCESS'
    except Exception as exc: direct=type(exc).__name__
    opened, wb, pid=m.open_document(path)
    value=wb.Worksheets(1).Cells(3+i,2+i).Value2
    checks.append({'direct':direct,'value':value,'expected':121+i,'readonly':bool(wb.ReadOnly),'exact':Path(wb.FullName).resolve()==path.resolve(),'owned_pid':pid,'unchanged':before==hashlib.sha256(path.read_bytes()).hexdigest(),'prompt_input':False})
    wb.Close(SaveChanges=False);opened.Quit()
(out/'operator-open-proof.json').write_text(json.dumps({'checks':checks,'method':'real Excel COM; not independent human-visible confirmation'},indent=2),encoding='utf-8')
print(json.dumps(checks))
