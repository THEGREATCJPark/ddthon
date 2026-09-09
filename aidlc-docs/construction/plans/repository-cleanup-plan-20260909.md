# Repository branch and PR cleanup — approved maintenance

Recorded: 2026-09-09T06:56:49.257562+00:00
Base main: `123fb49b6b4b02190d6074baba11a6e44e24d155`. Current MVP acceptance remains complete.

## Intent, approval and scope

The preceding review proposed closing outdated U2 documentation PRs with current evidence, correcting the stale Replay test explanation, deleting seven fully merged development/QA branches, and retaining all Skill storage/demo branches. The user explicitly authorized that proposal: **“어 다 정리해줘”**.

This file records the already-approved scope before file corrections or remote deletions. It does not invent a prior artifact approval. Existing Inception, contracts, and unit ownership remain in force; CJ performs the agreed documentation integration under the completed A/B handoff and p1-scenario-correction-plan. No runtime implementation, new test logic, security fix, UI feature or Skill data change is included. The separately discussed pip target issue remains unimplemented.

## Impact and validation

PR #2 is an old contract comparison: environment access now returns a workbook snapshot; local task mapping and S2 own business interpretation. PR #3 describes an old single-instance limitation; current access code enumerates registered running documents by exact path. Preserve both original documents and their author/commit/blob/hash metadata before removing source branches. Correct only the inaccurate `read_spec` docstring in `tests/test_replay.py`.

Security/resiliency extensions remain disabled as recorded in state; normal preservation and approval requirements still apply. Partial PBT is unchanged/N/A to documentation and branch references. Relevant existing Replay/access tests, docstring-stripped AST equality, runtime/rule tree equality, archive byte hashes and remote reference verification are the required checks. No new Excel session or live scenario is needed.

## Execution sequence

- [x] 1. Read existing state/rules/approved contracts, verify branch ancestry and capture remote heads plus user authorization.
- [x] 2. Preserve original PR documents in `aidlc-docs/history/u2-pr-review-20260909/`; write current disposition in `aidlc-docs/construction/u2-p1-git/pr-review-disposition.md`; correct the one test docstring.
- [x] 3. Validate unchanged executable behavior and historical bytes, run existing relevant tests, and deliver documentation/test-comment changes to main with concurrent work preserved. Delivered in `481d7a0`; existing targeted tests: 18 PASS / 1 opt-in SKIP, runtime/rules unchanged.
- [x] 4. Comment and close PR #2/#3 as superseded after main preservation. Delete the seven merged branches and the two archived documentation branches only while each remote SHA still equals the reviewed SHA. Preserve all nine Skill/demo branches and every local checkout.
- [x] 5. Verify remote PR/branch state, record actual results and update audit/state; deliver the final maintenance receipt to main.

## Branch policy

Deletion candidates: `codex/development-closeout-20260909`, `codex/team-hub`, `work/u1-p1`, `work/u2-p1-git`, `qa/embed-20260909-1120`, `qa/embed-20260909-1315`, `qa/embed-20260909-1430`, `docs/u2-integration-contract-diff`, `docs/u2-known-limitations`.

Keep `main`, `team-skill-store`, `team-skill-demo-20260909` and all seven existing `codex/p1-*` storage/demo branches. They contain runtime data and/or recorded publication evidence, not unmerged application implementation. Do not merge their data roots into main or infer test failure from their divergence.
