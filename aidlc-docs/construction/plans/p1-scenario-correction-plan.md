# P1 scenario correction / approved continuation

User approval (raw): 좋아 그럼 이제 계속해서 진행해봐.
This executes the immediately preceding eight-step plan and the NASCA(가상) naming decision. Existing CONSTRUCTION continues; no retrospective approval or Inception restart. Product human candidate approval is not granted by this development approval.

## FD / contract correction (FR-P1-1/5/6/7, FR-SKILL-4, FR-USAGE, US-P1-1..4)
- Shared procedure is exactly action=file-access, method=excel-com-attach. Workbook path, sheet/column/row selection, values, OLS and chart stay in local task context.
- B access returns a workbook snapshot (sheets with names, used-range origins and cell values); capability verification checks successful fresh read and unchanged original, not production-data shape.
- S2 interprets a local task mapping (sheet, month column, value column, first row), computes the approved three-point OLS and produces a local chart. Missing mapping returns NEEDS_TASK_MAPPING with a local artifact for Agent inspection; never guesses a hardcoded layout.
- Replay re-reads current target and verifies content identity plus capability, independently of task mapping; old first-run artifacts are not inputs.
- Reuse requires freshly recomputed digest and explicit exact execution confirmation plus S3 eligibility: valid local review+Replay or imported remote publication evidence. Locally rejected/proposed/blocked candidates are not normal reuse. Remote evidence does not create receiver approval/Replay.
- Environment metadata labels 사내환경 / NASCA(가상); it is supplied context, not observation or automatic diagnosis; no solution/password. Search precedes new discovery.
- P0 remains working throughout. Two-package minimum generalization is a subsequent explicit step; exact approval digest validation is never removed.

## NFR / technology decisions
Existing Windows Python/pywin32; openpyxl for real standard direct reader, matplotlib for local PNG chart; explicit optional p1 dependencies. No web hosting or new framework. Task data/artifacts stay local and out of exported descriptor/events. Partial Hypothesis applies to digest, serialization, task mapping/OLS invariants. Official rule files unchanged; disabled security/resiliency extensions stay disabled while approved NFRs remain enforced. Add Windows Python CI with fixed Hypothesis seed; Excel real test separately opt-in.

## Code Plan (before implementation)
- [x] 1. Preserve all current source/docs/evidence and user README/EVALUATION edits outside repository.
- [x] 2. Correct envharness_p1, reuse_service, replay, publish_pipeline and experience_service contracts and tests; CJ integrates completed A/B handoff (no concurrent writers).
- [x] 3. Add local task mapping/chart and CLI; revise C9 environment instructions and invalid P0 unrelated fixture.
- [x] 4. Regression tests: corrupt digest invokes no runner/count, rejected candidate cannot reuse, remote proof works without local review, COM failed read != NOT_RUN, offset/different-layout capability, candidate contains no schema/data.
- [x] 5. Isolate real Excel initialization vs open/read; bounded subprocess logs, never kill user Excel. Run direct/read/Replay using explicit prepared files.
- [x] 6. Fresh Agent Cold, human exact approval, real GitHub publication and fresh Warm. Human approval remains an explicit user action; incomplete gates remain NOT_RUN.
- [x] 7. P0 two-package minimum generalization and verification.
- [x] 8. Integrate original A/B Git ancestry, CJ deltas, final tests/docs/README/evidence, push reviewed tested baseline. Preserve team-hub; do not delete branches.

## Testable properties
Descriptor digest unchanged by task mappings/data (task context excluded); actual values permuting sheet offsets leaves extracted task rows unchanged under corresponding mapping; OLS linear oracle / nonnegative forecast; round-trip existing PBT retained. Failure logs append, not replaced by later skips.

## P0 minimum-generalization implementation detail (approved step 7)
Keep legacy run-p0 and its exact fixture behavior. Add optional operator-authored local --policy to apply-requirements: approved exact refs, named local package sources, distribution-to-import mapping. One pinned requirement is parsed from task input; its version/import are task facts. Environment-only Skill declares pip-install and source name, no target/version. Without --policy legacy exact-demo approval remains. Reject URLs/options/unpinned/multiple inputs; this is not a universal package solver. S1 receives explicit pip_task and reuses the same install/version/import verification. Add two generated harmless wheels using the same descriptor/digest, different requirements and clean workspaces. Never let the Agent author its own approval policy.

Current validation: initial diagnostic Cold followed by actual human exact approval, different-workbook Replay PASS, GitHub publication and new Agent Warm PASS. Three additional frozen-source Cold sessions PASS. Step 8 completed with original A/B ancestry preserved and baseline 96f3c85 pushed; acceptance evidence follow-up is separately recorded. Whole-product submission review and B-PC demonstration remain pending.
