# P1 Claude Code approval selector correction

## Context and authorization

Current phase: CONSTRUCTION / integrated Build & Test. User reported a real round-1 dialogue that completed the task and created a candidate but ended with a prose sharing question instead of the requested CLI selector. User explicitly requested this correction while following AI-DLC. This is a bounded correction of the already approved operator-open-org-cold Code Plan step 6 and CLI approval amendment, not a new lifecycle or a fresh feature plan. No retrospective approval is asserted.

Traceability: US-P1-4 / FR-P1-7 / C9 dialogue to S3 human review. Exact candidate human approval, independent Replay and successful remote push remain required. This development instruction is not candidate publication approval.

## Implementation and validation sequence

- [x] 1. Preserve existing round Skill instructions and input/store/usage hashes before changing instructions. Keep original user run and candidate untouched.
- [x] 2. Update `.claude/skills/skillloop/SKILL.md`: require an actual AskUserQuestion call in interactive Claude Code after showing real candidate content/ref/reviewer/destination. Prose alone is not the requested selector. Use approval/hold options, no automatic selection, no approval files before user response. If tool unavailable/denied, remain pending and report the limitation.
- [x] 3. Refresh only the Skill instruction copy in the three prepared round workspaces. Record hashes and a mid-session protocol amendment; round 1 used the old instructions until this correction and is not an unchanged-protocol run. Do not reset or rerun the task.
- [x] 4. Run existing review/publication gate tests, verify unchanged work data and instruction copy identity. Do not claim a real selector was displayed without a live user confirmation.
- [x] 5. Record audit/state and give a continuation prompt that reloads updated instructions and requests the selector for the existing candidate. No model task execution, approval or publication by this operator session.

## Limits

The host Claude Code renders the native selector; Markdown instructions cannot create that UI on their own. Tool invocation in the live session remains the acceptance check. No Windows GUI, new permission bypass, product gate changes, website changes or new automated benchmark work. Security/resiliency extensions retain prior opt-out; existing NFRs remain applicable. PBT is not newly applicable to this instruction-only change; existing gate regression is retained.

Validation: existing tests/test_p1_services.py and tests/test_p0_publication.py completed with exit 0. Three Skill copies identical; eight readable data hashes unchanged. Round1 workbook hash unavailable because the user's Excel holds it; no close or unlock attempted. Real native selector display remains USER_VERIFICATION_PENDING. This correction does not approve or publish the existing candidate.
