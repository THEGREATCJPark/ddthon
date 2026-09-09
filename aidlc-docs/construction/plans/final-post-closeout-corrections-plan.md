# Final post-closeout corrections — proposed bounded scope

Recorded: 2026-09-09T07:16:39.489586+00:00. Reviewed main: `b54e6947eb53688f6aa6cb289963ad96d5330898`.
**APPROVED — implementation in progress.**

## Decision scope

This consolidates the pending [ZIP compatibility plan](submission-zip-build-compatibility-plan.md), the latest QA feedback, and the earlier unimplemented pip-target review. Existing MVP acceptance is retained. The user explicitly excludes the prior evaluation's priorities2/3 (effect headings/comparison display and gallery/Warm wording); those remain excluded.

Recommended implementation bundle: ZIP build compatibility, locale-portable test configuration, bounded CLI operational-error handling, and the previously confirmed pip-target validation gap. Each remains separately traceable; no past result or QA score is silently overwritten.

## Findings and dispositions

| Item | Decision |
|---|---|
| F19 original ZIP | Accept build dependency problem; reject deleting original evidence. Replace only the build-time ZIP import with the verified commit-pinned GitHub URL. Existing media remain bundled individually. |
| Locale portability / F11 | Accept. Native cp949/UTF8-mode0 reproduction: one targeted test FAIL, pip --version exit2 with invalid cp949 characters in its generated pip.ini. Existing 200/2 CI uses explicit PYTHONUTF8=1; its PASS remains valid for that condition. Do not claim a new full-suite 199/1/2 run. |
| F4 CLI errors | Accept bounded behavior correction. Malformed store JSON currently produces a raw traceback in match with exit1. A broad catch-all is not a safe one-line fix; handle operational failures at the command boundary and preserve failure status. |
| Earlier pip-target candidate | Include as a separate small S1 correction in the proposed bundle. Invalid options, URL/path references and ambiguous archive/wheel strings must not reach the install call. Actual exploit execution remains NOT_RUN. Format validation does not solve remote-Skill trust. |
| F20 account name | No blanket replacement in audit/history/screenshots. The account identifier is not a credential; byte/hash provenance would be affected. Privacy-redacted public copies would be a separate request, not an in-place rewrite of original evidence. |
| F15 Firebase web key | Do not move to env solely to mark a security finding resolved. Firebase documents these identifiers as public by design; authorization depends on rules/IAM/App Check and appropriate restrictions. This review does not claim cloud-console restrictions were audited. Source: https://firebase.google.com/docs/projects/api-keys |
| F12 README template | User already supplied the submission template/FAQ text. Compare actual README headings against that source if needed; absence of a particular QA-local filename is not proof that the template is unavailable or that evaluation is impossible. No new external capture is required for this change. |
| chat-logs gate | No empty directory or invented logs. Example layout is not a mandatory scoring gate established by the supplied guide; current authentic audit and evidence remain. |
| F17 / F18 / F6 / F7 | No change or status closure inferred. Off-main Skill data branches remain intentional. Insufficient context for unexplained IDs F6/F7 to prescribe changes. |
| P0 comparison display set | Explicitly excluded with the prior priorities2/3. Preserve current original data and disclosure; no relabelling or headline edit. |

## Minimal changes and acceptance criteria

### A. ZIP delivery compatibility

Files: `team-hub/src/P1Media.tsx`, `SUBMISSION.md`, associated result records. Follow the pending ZIP plan: keep original ZIP and its hash, use a literal commit-pinned raw URL, preserve MP4/PNG/SRT/logs. Verify normal build and a separate source copy that never contains files over10MB. Confirm rendered P1 media and the original download link. No new storage service, package or release asset.

### B. Locale-portable test fixture

Files: `tests/test_p0_scoped_auto_reuse.py`, same-pattern `tests/test_p0_two_packages.py`. Preferred change: write the local find-links directory as an ASCII percent-encoded `file:` URI (`Path.resolve().as_uri()`) instead of raw non-ASCII filesystem text in pip.ini. Keep the actual Korean/spaced work path and test assertions unchanged. Do not rename the test path to ASCII, skip the test, change expected ENV_NOT_READY to success, or solve the test merely by forcing UTF-8 mode.

Verify the existing cold Git-received Skill test and two-package test under native cp949/UTF8-mode0 and UTF8-mode1; actual offline failure → authorized reuse → install/version/import → count1 and already-installed count unchanged must still hold. Cross-platform local URI behavior must remain valid. If a broader product defect is discovered, report it rather than silently expanding this fixture correction.

### C. CLI operational failures

Files: `skillloop/cli.py`, focused tests in `tests/test_cli_errors.py` (new, explicit boundary assertions only). Preserve existing per-command validation and exit codes. At the command dispatch boundary, handle explicitly expected file/configuration errors and bounded subprocess timeouts with a short actionable error on stderr and a nonzero exit. Do not catch all BaseException/Exception indiscriminately, swallow programming assertions, convert failures to success, reset stores, or manufacture counts. Preserve argparse help/error behavior and normal KeyboardInterrupt semantics.

Required tests: malformed store JSON and mocked unreadable file / timeout produce controlled failure; normal dispatch result is preserved; unexpected programmer error propagates; no count/store mutation is introduced by error presentation. Detailed exception type/context should remain useful; a global traceback suppression flag or new logging subsystem is out of scope.

### D. Pip install target validation

Files: `skillloop/reuse_service.py`, `tests/test_reuse_service.py`. Use the existing supported bare distribution-name contract for the legacy pip_task=None path, without adding new name==version support. Validate before the installation call; reject options, URL/direct references, absolute/relative paths and names pip can interpret as local archive/wheel inputs. A regex that only rejects slashes and leading '-' is insufficient (bare .whl/.tar.gz inputs were observed in the earlier review). Keep the observation, bare name passed to pip show, and existing expected-version/import checks coherent. Keep the task-driven policy branch and P1 behavior unchanged.

Required tests: invalid values never invoke the install function, including malformed types/options/URL/path/archive cases; normal seed succeeds; a valid nonexistent distribution remains a genuine install failure with no counted reuse; no digest policy is copied or weakened. Exact regex/parser details must be checked against existing supported calls, not advertised as universal package resolution or full remote trust hardening.

## AI-DLC and execution order

The existing scenario correction plan records completed A/B handoff and CJ integration. CJ remains the single maintainer for this follow-up; do not ask A/B to edit the same files concurrently. Requirements/architecture/Units are not restarted. This is minimal post-acceptance FD/NFR/Code Plan adaptation under existing installation-integrity, failure reporting and reproducibility requirements.

Security/Resiliency extension opt-outs stay as recorded; ordinary input integrity still applies. Partial PBT requirements stay in force for the existing digest/serialization/dedup properties. New CLI/fixture examples are focused regression cases, not stand-ins for a new exploit campaign.

- [x] 1. Read current source and QA claims; reproduce native cp949 fixture failure and malformed-store traceback using disposable test data. Preserve pre-fix logs.
- [x] 2. Obtain explicit approval of this four-item scope; append the user's exact approval. Existing final MVP acceptance and prior branch-cleanup authorization are not implementation approval for this bundle.
- [ ] 3. Implement B, D and C in separate reviewable commits; validate each related contract before proceeding. Implement A with the pending ZIP plan. Preserve concurrent web changes and excluded presentation text.
- [ ] 4. Run affected tests under both encoding modes, then final Python regression under documented UTF8 mode and native cp949 mode with real Excel opt-in disabled. Run existing web tests plus normal/filtered builds. Preserve actual failures and condition-specific counts; do not target a predetermined PASS count.
- [ ] 5. Review diffs for preserved original media hashes, product approval/dedup behavior, unchanged excluded presentation, and official rule files. Record actual SHA/results/limitations and request final result acceptance/main-delivery approval appropriate to the user's scope.
- [ ] 6. After authorized delivery, verify GitHub CI and append final evidence while retaining the already-accepted MVP baseline. No new P0/P1 agent filming, live Excel trial or submission-site upload is part of this bundle.

Pre-fix diagnostic evidence: [planning diagnostics](../../history/final-followup-planning-20260909/README.md). No product/test implementation changes, commit or push have been performed for this proposal.

Approval received 2026-09-09T07:18:49.269422+00:00: user “어 진행해봐 빠르게” approves this four-item plan. CJ performs the already-transferred maintenance; original A/B authorship remains preserved. Concurrent main70387ef web presentation edits are retained, not reworked by this task.
