# P0/P1 integration and acceptance

P0: follow scripts/prepare-p0.ps1 and ask a new Claude session to install the workspace requirements.txt. Verify real initial failure, observed-signal MATCH, installation/version/import in the same work venv, exact run_id event once, and no new candidate. The three previous natural-language reproductions and their failed first attempt are retained in result/p0-reproduction/. Additional two-package same-Skill verification is in tests/test_p0_two_packages.py and scenario-correction results.

P1 Cold: scripts/prepare-p1.py creates encrypted files and keeps them open. Use a new workspace/store that has no file-access Skill. Ask only for the spreadsheet production forecast. Verify actual direct failure, real NO_MATCH, Agent discovery, read-only workbook access, task-specific mapping, actual3+forecast1 chart, candidate+1 and reuse+0. Environment facts must not include solution or task mapping. Do not silently reset an existing workspace to pretend a fresh run.

P1 lifecycle: a person reviews the exact candidate ref. S3 records that actual decision. Independently read a different workbook using C6; only actual PASS permits Git publication. Confirm remote branch commit, then pull to a separate store and verify receiver approval/Replay remains absent. A user must explicitly authorize execution of the imported exact Skill.

P1 Warm: a fresh Claude session interprets a different task layout, reuses the imported Skill, completes task/chart, records +1 and creates no duplicate candidate. Share the event through Git, pull twice and verify one imported event then zero duplicates. Check original workbook hashes before/after. Use different PC reproduction for the final team demonstration; separate workspace testing on CJ PC does not establish B-PC readiness.

Current evidence: result/p1-acceptance/. B-PC steps: b-github-demo-guide.md. Additional Cold runs are independent agent sessions, not independent human authors. Test profiles/oracles stay outside the Agent workspace. Raw private reasoning/signatures are excluded from public traces; actual tool actions/results and failed attempts are retained.

No quantitative performance requirement was approved; load testing is N/A. Security checks in the regression cover digest/gates, non-sensitive bundles, read-only access and UI paths; a full penetration test is not claimed. UI visual review and B-PC reproduction must be reported separately from programmatic tests.
