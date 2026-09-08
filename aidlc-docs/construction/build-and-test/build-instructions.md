# Build instructions — Windows checkout

Use the latest main checkout. Preserve existing work; use a new folder when reproducing on another PC. Python, Git and a Windows-native terminal are required. Desktop Excel is required only for actual P1 application access.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[p1]" -r requirements-dev.txt
.\.venv\Scripts\python.exe -m skillloop --help
```

The repository checkout supplies fixtures; standalone wheel-only demo distribution is not claimed. Python CI installs declared dependencies on Windows. Build verification for the existing baseline includes actual editable installation and Python CI run 34235737366 (success), not just importing files from a dirty checkout. No production deployment is in scope.

Excel errors: use Desktop Excel and pywin32 on Windows; keep operator-prepared workbooks open. Never replace missing Excel with a mocked PASS. GitHub operations require network and configured Git authentication; tokens are not source files. Claude acceptance uses the operator's existing Claude Code authentication without printing credentials.
