# U2 PR #2 / #3 — current disposition

Review recorded: 2026-09-09T06:57:43.780342+00:00. Baseline: `123fb49b6b4b02190d6074baba11a6e44e24d155`. User-authorized post-acceptance repository maintenance; runtime behavior unchanged.

The original B findings are preserved byte-for-byte in [history](../../history/u2-pr-review-20260909/README.md), with author and commit metadata. Closing the PRs does not withdraw or erase those findings.

## PR #2: contract comparison

Original: [PR #2](https://github.com/THEGREATCJPark/ddthon/pull/2), `43282aab483bd12ff08c17b55323359ba4ad9df9`, reviewed old main `0041d87`.

| Original observation | Current decision and evidence |
|---|---|
| AccessResult.content changed from production rows to a workbook snapshot | Intentional approved contract correction. [Scenario correction](../plans/p1-scenario-correction-plan.md) separates reusable environment access from local task data; [integration contract addendum](../plans/p1-cj-integration-contracts.md#current-contract-correction--scenario-continuation) explicitly supersedes the earlier schema. |
| procedure no longer chooses sheet/columns | Intentional: shared procedure contains action/method only. The current document's sheet/column/row mapping is local task context interpreted by S2. Restoring shared task coordinates would contradict the corrected scope. |
| The Replay test only proves forwarding, not read_spec behavior | Accepted. Correct the stale test docstring to state that it verifies forwarding and the substituted access result. It does not prove live Excel behavior or sheet/column selection. Assertions and runtime are unchanged. |
| Access success no longer requires three completed months | Intentional layer separation. C7/S1/C6 validate fresh readable workbook access and read-only evidence; S2 validates actual task rows, OLS and chart. Access success alone does not prove task completion. |

Disposition: preserve the old comparison, apply the documentation correction, then close as superseded by the approved scenario/integration contract. No original task-specific schema restoration and no new live-test claim.

## PR #3: empty Excel instance

Original: [PR #3](https://github.com/THEGREATCJPark/ddthon/pull/3), `c53158c001d88710d076138bd383d9a395c35a16`.

The old finding was valid for its single-GetActiveObject path. Current `skillloop/envharness_p1.py::_read_via_excel_attach` also enumerates `GetRunningObjectTable().EnumRunning()`, checks both moniker and workbook FullName against the exact target path, and reads an already-running object. It deliberately avoids `GetObject(path)`/opening a closed workbook. Existing [operator-open correction records](../plans/operator-open-org-cold-code-generation-plan.md) describe this boundary and preserve the earlier Agent-generated reopening defect.

Disposition: close the old missing-enumeration claim as superseded. Unregistered/closed/inaccessible workbooks can still be unavailable; this review does not claim all Excel instance problems are solved. No live Excel regression was executed by the branch cleanup. Existing native demonstration evidence and its original conditions remain separate.

## Verification and delivery

Required checks: original document byte/hash identity, unchanged executable test AST after removing docstrings, unchanged product/rule trees, relevant existing Replay/access tests, and main preservation before closing/deleting the two PR heads. Actual results are recorded in [cleanup verification](../../history/u2-pr-review-20260909/verification.json) and the [maintenance plan](../plans/repository-cleanup-plan-20260909.md).

The P0 pip-target security candidate is a separate unimplemented follow-up. This cleanup does not resolve it or change QA scores, product gates or the accepted MVP scope.
