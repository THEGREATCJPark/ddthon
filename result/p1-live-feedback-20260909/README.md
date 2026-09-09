# P1 live feedback — user-led second turn and operator opening

Existing AI-DLC CONSTRUCTION / Build & Test; bounded Request Changes amendment recorded before code. User explicitly replaced a direct Excel question with a short failure/search report followed by user-provided environment facts. FR-P1-3 remains; US-P1-2 AC-1 trigger aligned. Original question-based acceptance history retained. Web untouched.

## First response
After actual direct failure + real NO_MATCH and only when the workspace provides this environment label:
사내환경 · NASCA(가상)에서 이 파일의 Python 직접 읽기에 실패했습니다. 팀 Skill 저장소에서도 관련 해결 방법을 찾지 못했습니다.
End turn without a direct Excel question or solution hint. User may then state that Excel can read it. Metadata alone never establishes actual app-open or a real NASCA cause. If user only asks for August actual data, the May–July sample has no August actual value;1650 is a forecast, never an observed August value.

## Operator viewing defect
Original preparation used an unretained random password and kept Excel open. A separate file open therefore required a password unavailable to the operator. Current old Excel process31792 was present, but exact Cold workbook was not found in read-only ROT enumeration; not enough evidence to say whether it was closed or unregistered. No old workbook was decrypted/saved/closed and no password dialog was automated.

New optional --ask-password prompts twice with hidden console input. Password stays in memory, is not a command-line argument or written to generated workspace/config/logs. Operator may reopen their own sample with that password; Agent still receives no password or decryption path. Default random-password mode is retained; Cold workbook activated and clear operator instructions printed.

## Verification
Initial targeted24 PASS. After password-length guard, final targeted25 PASS. COM-double tests check use of chosen password and absence from generated text/output, invalid empty/mismatched/overlength inputs, owned cleanup. These are not Excel/Agent execution evidence.
Actual first reopen test failed(com_error) and is retained in excel-reopen-verification.json. Microsoft SaveAs API documents at most15 password characters: https://learn.microsoft.com/en-us/office/vba/api/excel.workbook.saveas . API documentation only, no external preimplementation code used. New guard rejects overlength inputs before environment mutation, default random length14. Actual valid-password repeat recorded separately; its result must be read before claiming success.

Existing Cold/Warm C9 files refreshed; XLSX/store/usage/settings hashes unchanged (work-preservation.json). Active Claude sessions may retain old loaded instructions; use a fresh session for new narration. No fresh Agent Cold/UI transcript is claimed by these checks.

## User setup
PowerShell window1 (interactive, keep open):
```powershell
$env:PYTHONUTF8 = "1"
Set-Location "C:\Users\cik61\Desktop\ddthon-main"
.\.venv\Scripts\python.exe scripts/prepare-p1.py "C:\Users\cik61\Desktop\skillloop-p1-feedback-20260909" --ask-password
```
Choose a remembered demo-only password of1–15 characters at the hidden prompts. READY means workbooks are already open. Use that Excel window, or enter your chosen password when reopening. Do not tell Claude the password. Use a new destination if the path already exists; do not overwrite previous evidence.

PowerShell window2:
```powershell
$env:PYTHONUTF8 = "1"
Set-Location "C:\Users\cik61\Desktop\skillloop-p1-feedback-20260909\cold"
& "C:\Users\cik61\.local\bin\claude.exe"
```
First request for the complete approved forecast scenario:
AAAAA01_직전_3달_생산량.xlsx를 읽고 다음달 예상 생산량을 포함한 추세선을 보여줘.
After the failure/search report, user provides the fact:
이상하네, 내가 직접 Excel에서 여는 건 문제없는데? 한번 다른 방법으로 진행해봐.
Cold: do not sync a matching published Skill before this test. Actual May–July1200/1350/1500; August forecast1650; candidate1/reuse0 expected only after real access/work verification. Candidate is not publication.

## Final outcome
- Final26 targeted tests PASS, including noninteractive password input rejected before any echo fallback.
- Real Excel reopen automation did NOT pass: original attempt COM error; valid <=15-character attempt and explicit positional-argument attempt waited at an actual Excel password dialog. Computer Use inspected only the owned test window and cancelled its prompt with Escape so cleanup could finish. Keyword vs positional experiments and errors are retained; the15-character guard is justified by API contract, but has NOT been proved to explain the COM dialog.
- Preparation itself created encrypted workbooks and opened them; actual direct parser still failed. Closed-file reopen with the chosen password remains a USER CHECK, not an asserted PASS. No unrelated user Excel process was terminated.
- No new Agent Cold run validated the revised first reply. Candidate/publication/reuse evidence from prior runs is preserved; website excluded.
