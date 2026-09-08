# P1 scenario correction — current review evidence

User approved the eight-step continuation plan before implementation. Existing CONSTRUCTION continues.

## Implemented
- P1 content digest recalculated before execution; selected candidate with changed content cannot call runner or increment usage.
- S3 eligibility separates local unreviewed/rejected candidates from verified reuse; imported publication evidence does not generate receiver approval/Replay.
- Shared procedure is environment-only. Workbook snapshot preserves used-range row/column origin. Agent task mapping and chart stay local.
- COM unavailable and actual read failures remain distinct with stage/reason.
- Display context is 사내환경 · NASCA(가상), supplied environment description, not claimed error diagnosis.
- P0 optional operator policy supports a generic local package source Skill, with per-task version/import and exact approved refs. Two different generated packages reuse the same descriptor/digest; legacy demo unchanged.

## Actual execution
- Reproduced prior Excel timeout in Workbooks.Open after encrypted SaveAs. Preparation retains the already-open workbook; direct openpyxl failure + actual COM access + unchanged source test now PASS.
- Fresh Claude Cold received only the requested XLSX production forecast task. It observed failure/NO_MATCH, inspected format and application environment, discovered read-only application access and interpreted C/F columns at row6. Forecast1650 and actual PNG produced; candidate created, no reuse.
- Procedure schema validation message was improved during the diagnostic Agent execution; earlier rejections are retained. Do not call this a flawless first attempt.
- Human exact approval is pending. Replay→GitHub publish→new Agent Warm remain NOT_RUN. This approval is separate from development approval.

## Traceability and extensions
US-P1-1..4 / FR-P1-5..7 / FR-SKILL-4 / FR-USAGE are linked in scenario correction plan. Existing PBT02/03/07/08/09 retained; generated offset invariants and two-package real process cases complement round-trip/digest tests. CI fixed Hypothesis seed configured; remote CI execution not yet claimed. Disabled security/resiliency extensions remain disabled while approved NFRs remain implemented. No formal AI-DLC rules changed.

## Evidence
See result/scenario-correction/ for actual logs, candidate-review.json and cold-trend.png. The previous Excel FAIL_TIMEOUT remains in the older result directory and the current probe log.
