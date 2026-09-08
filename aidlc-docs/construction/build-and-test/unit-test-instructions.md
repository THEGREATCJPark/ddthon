# Unit and local integration regression

```powershell
.\.venv\Scripts\python.exe -m pytest --hypothesis-seed=20260908 -o addopts='' -q
```

Baseline 96f3c85: 139 passed, 2 skipped (267.31 seconds). One skip is opt-in real Excel and one is the absent-B-module scenario that is not applicable after integration. Exact source hashes and output are in result/scenario-correction/validation.json and final-regression.txt. These counts include local integration tests and must not be called 139 independent user scenarios.

Real Excel, separately opt-in:

```powershell
$env:SKILLLOOP_RUN_EXCEL_TESTS = '1'
.\.venv\Scripts\python.exe -m pytest tests/test_envharness_p1.py::test_real_excel_attach_end_to_end -o addopts='' -q
Remove-Item Env:\SKILLLOOP_RUN_EXCEL_TESTS
```

Baseline actual result: 1 passed. Earlier timeout and failed attempts remain in result/. Disabled extension suites are not implicitly enabled; approved security/resiliency requirements still apply. Partial Hypothesis rules remain active, with generators, shrinking and the recorded seed. New failure -> record it, correct the approved implementation, rerun the affected checks; do not change tests to reach a desired PASS count.
