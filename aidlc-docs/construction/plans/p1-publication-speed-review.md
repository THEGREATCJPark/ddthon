# P1 publication speed / measurement correction

Status: measurement boundary accepted and applied; Replay removal impact REVIEW REQUIRED. Current stage remains CONSTRUCTION / Build & Test. No product gate changed.

## User request and observed cause

User requests dropping publication Replay for the demo, reducing latency, and measuring through task resolution rather than publication. The actual session ae179f5e-1cd8-49ee-9ef0-ac9024f5bfbd shows WORK_COMPLETE at 04:25:31.762Z, a human AskUserQuestion approval, Replay PASS, then a Claude auto classifier denial before publish execution. Replay tool roundtrip was 2.699 seconds; denied publication tool roundtrip was 51.833 seconds. Removing Replay would not resolve that permission boundary.

## Measurement amendment — authorized now

For all retained manual runs, start at the actual task request, end at the first real completed work result including requested chart. Report user-facing result time separately. Include and separately identify user environment-fact waiting time. Human publication review, Replay, Git permission waiting and push are post-task metrics. Do not replace earlier raw logs or add old /cost totals to this truncated interval. Deduplicate native assistant usage by message.id, keeping input/output/cache-read/cache-creation separately. Mixed task-result/review-invitation messages cannot be split exactly; disclose this if using the user-facing cutoff. This is a retrospectively specified analysis boundary for this existing run, applied consistently to later and before-PC runs, not a preregistered endpoint claim.

## Recommended minimal implementation

1. Keep the existing exact human review / independent Replay / confirmed push semantics.
2. Preserve this approved candidate and completed Replay. Do not rerun task, review or Replay merely because publish was denied; before a later permitted publish, recheck exact candidate/evidence identity using the existing gate.
3. Resolve publication permission through the host's normal user-controlled approval mechanism. Do not have the operator agent rerun the denied write, disguise the command, add broad allow rules or switch to bypass permissions. Any granted execution permission is recorded separately from candidate approval.
4. Shorten redundant narration/help lookups where the verified existing CLI contract is already known; no solution hints for Cold discovery, no skipping result verification. Preserve machine evidence.
5. Demonstrate speed of reusing this discovered Skill in a separate Warm run after actual publication. Do not describe the Cold discovery duration as Warm reuse latency.

## If user retains the requested Replay removal

This changes FR-P1-7 (especially PASS and NOT_RUN clauses), US-P1-4, Application Design SHAREABLE/publication contracts, U2 design/NFR/Code Plan, S3 `_gate` and related C4 export eligibility, C9 and review/publication tests. It is not an environment-only fix. Proposed alternative is human-reviewed publication with explicitly recorded `Replay=NOT_RUN` and validation level `HUMAN_REVIEW_ONLY`; it cannot be presented as independently verified. Previously Replay-verified artifacts keep their real provenance; P0 rules are not silently relaxed. Required implementation sequence is scoped requirement/story/design amendment, Code Plan confirmation, gate/metadata/UI/test updates, then real publication and receiver tests. Never merely delete the `_gate` check or fabricate PASS.

Review decision requested: retain the fast existing Replay and address host write permission (recommended), or confirm the changed review-only publication contract above. Original user request is recorded; this document does not reinterpret it as approving the newly specified review-only contract.

## Actual result

result/p1-auto-cold-task-cutoff/round1-measurement.json records source log hash and times. Operator snapshot is preserved outside the repository. Direct result/forecast/chart available; chart visually inspected against returned 1200/1350/1500 and 1650 forecast, actual/forecast lines distinguished. Source workbook verification remains the recorded runtime evidence, not a newly executed decrypt/read. Candidate reviewed and Replay PASS; publication permission denied before execution, not a Git push failure.

## 2026-09-09T04:32:14.4565559Z — Recommended publication path approved
User: 그래 니 의견대로 진행해. 그리고 다시 cold test 해볼수있게 줘.
Decision: retain FR-P1-7 Replay and exact human review; review-only alternative not adopted. Prepare a new Cold with normal user-controlled host permissions (installed CLI calls this manual, not default), fresh P0-only Git branch, unchanged input, current C9, operator opener and preserved old results. No rerun of the prior denied publish by this operator. New workflow's remote write awaits actual user permission. Launcher records mode; unanswered-question timeout disabled for manual too. Measure task endpoint separately from publication. Part2 bounded setup authorized now; no new requirement or product gate.

## 2026-09-09T04:33:02.4298676Z — Manual Cold ready, real status checked
New root C:/Users/cik61/Desktop/skillloop-p1-cold-manual-20260909-133215; manual permission mode, human AskUserQuestion + Replay retained. New Git branch codex/p1-cold-manual-r1-20260909-133215 at P0-only baseline, input same. CheckOnly PASS and actual P1 search NO_MATCH. User reported old NASCA stored-Skill label: new store inspected contains only pip-install descriptor1, no file-access candidate, usage0. Initial status showed local mode because operator setup omitted sync-config.local.json; corrected via existing store-init against the already initialized mirror, no remote publication or data hiding. Re-rendered status reads actual Git metadata, no NASCA/Excel Skill. Receipt in new root/operator/status-before.txt. Old attempts/remote and round2/3 unchanged. PowerShell parse PASS; measured Agent/UI run NOT_RUN. No actual Excel opened by operator, Open-Document.cmd prepared for user.
