# Read an authorized Office workbook through the running Excel application

Use this procedure only for the user's exact workbook when ordinary file parsing
fails and an authorized Excel application already has that workbook open.

1. Resolve the requested workbook's full path. Record its SHA-256 and modification
   time before access. Do not decrypt, guess a password, or modify the original.
2. Attach to an existing Excel application through the Windows COM running object
   table. `win32com.client.GetActiveObject("Excel.Application")` may expose one
   running instance. Match each workbook's `FullName` to the requested full path;
   do not select `ActiveWorkbook`, a workbook by index, or just a matching filename.
3. If that instance does not contain the target, enumerate the running object
   table with `pythoncom.GetRunningObjectTable()` and inspect moniker display
   names for the exact target path. Bind only that matching existing object and
   verify its `FullName` again. Do not call `GetObject(path)`, `Workbooks.Open`,
   `DispatchEx` or another operation that opens a closed document or a new app.
4. On the exact workbook, read worksheet names and used-range coordinates and
   values through `Worksheets`, `UsedRange.Row`, `UsedRange.Column`, and
   `UsedRange.Value2`. Preserve the table structure; infer date/quantity columns
   from the actual content. No fixed worksheet, column, date range, or answer is
   assumed. Handle a single cell as a scalar and multi-cell ranges as rows.
5. Read only. Do not call Save, SaveAs, Close or Quit; do not change application
   settings, cell contents, formulas, formatting, or terminate any process.
   If no authorized matching open workbook is available, report that access is
   unavailable and stop. Do not open another workbook to produce an answer.
6. Recheck the original file's SHA-256 and modification time. A mismatch or access
   error is not a successful read. Keep retrieved business data and intermediate
   files in the current task workspace only. Perform the user's analysis from
   the retrieved data and explain the calculation used.

This provides an environment access procedure. It does not perform SkillLoop
search, Registry lookup, human approval, Replay, publication or reuse counting.
