
import win32com.client,win32process,os,tempfile,json
from pathlib import Path
from datetime import datetime,timezone
def mark(s,**kw):print(json.dumps({'stage':s,'at':datetime.now(timezone.utc).isoformat(),**kw}),flush=True)
mark('before-DispatchEx')
x=win32com.client.DispatchEx('Excel.Application')
mark('created',pid=win32process.GetWindowThreadProcessId(x.Hwnd)[1])
x.Visible=False;x.DisplayAlerts=False
mark('before-Workbooks.Add')
w=x.Workbooks.Add();mark('workbook-added')
s=w.Worksheets(1);s.Name='Data'
s.Range('C5:D7').Value2=(('2026-05',1200),('2026-06',1350),('2026-07',1500))
mark('values-written')
p=str(Path(tempfile.gettempdir())/('skillloop-probe-'+str(os.getpid())+'.xlsx'))
mark('before-SaveAs')
w.SaveAs(p,FileFormat=51,Password='temporary-probe-password');mark('saved')
w.Close(SaveChanges=False);mark('before-open')
w=x.Workbooks.Open(p,Password='temporary-probe-password');mark('opened')
from skillloop import envharness_p1 as h
h._excel_app=x
mark('direct',observation=str(h.attempt_direct_access(p)))
r=h.run_file_access_procedure({'action':'file-access','method':'excel-com-attach'},h.EnvContext(p,True))
mark('read',ok=r.ok,content=r.content,evidence=r.evidence)
w.Close(SaveChanges=False);x.Quit();mark('closed')
