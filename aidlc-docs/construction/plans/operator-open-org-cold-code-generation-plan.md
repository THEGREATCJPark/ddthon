# Operator open + organization-backed P0/P1 Cold — Code Generation Part 1

Status: APPROVED — Part 2 implemented; actual organization setup complete. Final regression165 PASS/2 SKIP; setup checks15 PASS. Implementation5fff0c4 pushed. User live P1 acceptance pending. Historical planning decisions below are qualified by the actual approval/correction sections at the end.

## 1. Request and current baseline

Continue existing CONSTRUCTION / integrated Build & Test. User requests a plan before implementing (1) password-free operator viewing without scripted/overfit Agent discovery and (2) organization-backed P0 followed by P1 Cold discovery and user publication. Website work is excluded.

Baseline: main 0041d87b8c1b701f1885c0cbd290031506c6a75c. Existing untracked result/b-github-receive-20260909 is preserved, not adopted or staged by this plan. A/B ownership handoff remains unchanged; CJ integrates existing modules.

User-provided transcript: C:/Users/cik61/.codex/attachments/338812f9-dd1e-4d6f-a0f0-c20962fab5ce/pasted-text.txt. This is reported execution evidence, not a newly executed local test. Expanded shell commands are not present, so the transcript alone cannot establish how Excel opened without a prompt or which instance was used.

## 2. Findings accepted from the transcript and source

- Natural task request, failure/NO_MATCH report, user-provided environment fact and reported July actual value 1500 are useful progress. Candidate is reported, publication is not complete.
- Reading the supported adapter before forming a discovery hypothesis risks obtaining the answer from product implementation. Agent should investigate available applications/document access first; API help can translate an independently discovered method into the execution contract afterward.
- OLE header does not prove NASCA or encryption by itself. User-approved NASCA screen wording is confined to explicitly configured demo context; no fabricated installed-program detection evidence. Implementation/provenance retain Office encryption and virtual context.
- Response includes internal terms (product CLI, adapter, procedure, task-mapping) and an unsolicited August forecast/chart for a July lookup. Default user response should answer the requested value; detailed traces and optional generated artifacts remain in evidence.
- Review failed at interactive input despite an explicit reviewer message; the response also mistyped the full digest. Exact identity must come from the descriptor, never a manually rewritten chat string.
- Current work context lacks remote/mirror, preventing publication. Supply transport configuration before the task, not at the last gate.
- Existing team-skill-store contains a published P1 descriptor and prior events. It cannot honestly serve as a no-P1 Cold database.
- gitsync, publish_pipeline and org_aggregator hard-code team-skill-store. A new demonstration branch requires aligned configuration and provenance, not a UI-only filter.
- Current Replay/S3 gate expects Excel read-only evidence. Publishing a P0 descriptor requires an actual pip Replay path; do not fabricate workbook fields or bypass the publication gate with direct JSON.

## 3. Bounded impact / traceability

| Change | Existing requirements / stories | Planned document alignment |
| --- | --- | --- |
| Operator no-prompt open, owned Excel readiness | FR-P1-1/3, NFR-RUN-1 P1 exception, US-P1-1/2 | U2 FD/NFR: opening is environment preparation, not Agent discovery or Replay |
| Explicit organization demo branch and consistent stores | FR-SYNC-1/4/5, FR-ORG, US-P1-4, US-UI-1/2 | Minimal FR-SYNC-1 and FR-P1-7 deployment wording; C4/S3/C10 context binding |
| Real P0 publication / remote reuse | FR-P0, FR-SKILL, NFR-SEC-4, US-P0-1 | Replay action-specific evidence, local source policy, exact remote execution confirmation |
| Human review UX | FR-P1-7, US-P1-4 | Review interaction changes, human decision / exact candidate / Replay requirements unchanged |

No new Unit, cloud service, NASCA driver, S3/DB adapter or website feature. No wholesale Inception restart. This review covers the minimal impact decisions and the implementation plan together. On approval, align the named current documents before code; preserve prior approvals and factual history. Any materially different mechanism requires a further bounded review.

## 4. Design decisions proposed for approval

### A. Operator viewing without password entry

Retain encrypted XLSX bytes so ordinary direct parsing actually fails. Add an operator-only document-opening entry point outside the Agent workspace. It uses the public fixture password nowhere to open the exact workbook, or activates that exact already-open workbook. User clicks the prepared entry point without entering a password. This is not a claim that arbitrary encrypted XLSX double-click works without supporting software.

The first implementation step is a bounded real Excel proof: closed workbook -> operator open without input -> correct workbook visible/readable -> direct parser still fails. Existing COM reopen failures remain recorded. If the no-prompt proof fails, stop this track as FAIL/BLOCKED and report the actual cause; do not convert to plaintext, feed a password to the Agent or implement a security driver as an unapproved workaround. Git integration can continue independently.

Preparation supplies only environment facts, file and transport locations. No COM method, sheet/column mapping, expected answer, password or recovery script goes in the Agent context. The opener does not compute, search, generate a candidate or increment reuse. Use full workbook path to distinguish multiple Excel instances, never ActiveWorkbook as identity. Leave unrelated Excel processes/workbooks untouched. Environment preparation does not count as discovery.

### B. One active organization database, P0 present / P1 absent

Proposed remote: https://github.com/THEGREATCJPark/ddthon.git. Proposed new demonstration data branch: team-skill-demo-20260909. It is a data branch, not a development branch. Keep existing team-skill-store and its genuine history unchanged. If the proposed branch already exists, inspect it; never overwrite/reset it to manufacture a Cold run.

The new branch starts with only the P0 descriptor, published after exact human review and fresh pip Replay. No P1 descriptor, file-access applicability or P1 usage event is copied. No fabricated 20-use history. Initial reuse is zero unless real preparation executions were counted, in which case report the actual baseline.

Extend GitSyncAdapter branch configuration with existing team-skill-store default. Bind mirror marker, fetch/push ref, transport evidence and lifecycle/aggregation to the explicitly selected remote + branch. Validate Git ref input and mirror identity. Do not replace the hard-coded equality check with acceptance of arbitrary unverified remote strings. Existing default-branch data and clients remain compatible.

P0 and P1 Cold receive the same selected organizational branch through independent local mirrors/stores/usage. Before testing, sync and show database scope, branch revision, Skill inventory and last-sync. The database is real Git-synchronized local data, not a fake UI counter. P1 Cold must search that database containing P0; it must not secretly search a different empty store.

After the user publishes P1, the same branch contains P0 + P1. Subsequent matching P1 runs are Warm. Preserve those records; repeated Cold validation uses separate, named test remotes/branches, not deletion of the user's published Skill. Do not publish P1 into the final live branch during automated preparation or dry runs.

### C. P0 shared Skill and action-specific Replay

Use the existing environment-only pip source policy where possible: descriptor refers to an approved source alias, local policy resolves that alias to a permitted path. Do not share absolute workstation paths or infer trust merely from a known fixture digest. An unknown source or changed exact reference must require confirmation or fail, never fall back to an allow index.

Add a pip Replay adapter that reuses S1 verification in a separate prepared verification environment and records actual install/version/import outcomes for the exact candidate. Replay is not a reuse event. S3 verifies action-specific evidence: pip evidence for pip-install, unchanged existing workbook/read-only evidence for file-access. Unknown actions, action/evidence mismatches and caller-supplied PASS must fail. Keep human approval, digest equality and confirmed remote push mandatory for both.

### D. Review once, without digest transcription

Provide an operator-facing confirmation step that displays current exact candidate content/ref and reviewer, then records one explicit human approval bound to that exact ref. It may accept a short interactive choice rather than manual typing of 64 digest characters. Re-read identity at recording time; content changes invalidate the pending review. Keep the existing terminal path compatible where practical.

The Agent can prepare the review and continue after the receipt, but cannot synthesize the user's confirmation, pipe an automatic yes or equate a generic publish request with exact review. Tell the user about this single operator confirmation before the live run. A plain chat approval is not silently upgraded into the old CLI's missing interactive evidence. Following approval: fresh Replay -> actual push -> read back remote result. Configuration supplies remote/mirror/branch ahead of time. New plan approval does not approve any candidate.

### E. Natural output and non-overfit discovery

User-facing messages describe task, observed failure, search result, next investigation and completed result. Keep raw CLI fields, full digest and developer contract details in logs/review surfaces. Do not force a particular successful sentence or guarantee discovery of COM. No source-code or adapter enumeration as the initial solution oracle; user facts and actual environment inspection precede binding to product API.

Preserve requested NASCA presentation only for the configured demo, with true provenance in records. For July lookup, report the actual July value and candidate/publication status; do not introduce an unsolicited August forecast. For missing actual month, report absence; forecast only when requested. No fake proxy/timeout explanation for P0 package-not-found.

## 5. Code Generation Part 2 — approval required

- [x] 1. Align impacted FD/NFR, Requirements deployment wording, Application Design contracts and current plan/status; preserve historical documents/audit. Record actual starting SHA and concurrent work before edits.
- [x] 2. scripts/prepare-p1.py and new scripts/open-p1-document.py: implement/test operator-only exact workbook open/activate and no-prompt proof. Add tests/test_prepare_p1_operator.py coverage for identity/readiness/failure; record live proof separately from test doubles. If infeasible, stop only this track and report.
- [x] 3. skillloop/gitsync.py, publish_pipeline.py, org_aggregator.py, cli.py: selected branch + registered transport context through initialization, sync, publication, reuse eligibility and status; preserve old default behavior. Add tests/test_org_demo_transport.py and relevant existing regression cases.
- [x] 4. skillloop/replay.py and publish_pipeline.py: action-specific real pip Replay using existing reuse_service/envharness contracts; no new matching/install implementation. Add tests/test_p0_publication.py for positive and negative gate cases, rerun P1 gate/Replay tests.
- [x] 5. cli.py and new scripts/prepare-org-demo.py: explicit operator review, common work connection metadata including remote/mirror/branch, exact execution confirmation and local source policy. tests/prepare_p0_work.py and scripts/prepare-p1.py get an opt-in organization preparation mode which imports from the selected branch rather than locally seeding the answer. Existing local demo preparation remains available.
- [x] 6. .claude/skills/skillloop/SKILL.md: concise discovery/review handoff, correct exact digest retrieval, requested-month response and transport-context usage. No product-code solution discovery, password/operator-opener access or staged success claims. Tests check behavioral boundaries rather than full fixed prose.
- [x] 7. Run focused tests, enabled PBT and full Python regression once final code is stable. Run automated integration against isolated test Git remotes and separately retained operator Excel workbooks. Preserve original errors and distinguish real Excel, substitutes, Agent transcript and transport evidence.
- [x] 8. After exact P0 human approval + pip Replay, initialize the final live branch with P0 only. Verify fresh P0 and P1 receivers: remote P0 present, P1 absent, hashes/last-sync/usage baselines recorded, statusline same context. Do not run the final P1 discovery or publication on behalf of the user during preparation. Deliver a verified-path command guide for P0 and the user-led P1 Cold -> review -> Replay -> publish flow.
- [x] 9. Save logs and run manifest under result/operator-org-cold-20260909/, update aidlc-docs/construction/build-and-test/build-and-test-summary.md and aidlc-state.md, append audit with fresh UTC for each event. Commit/push scoped product/docs/evidence after review of the diff; do not change website or unrelated B receipt. Identify pending user steps and do not claim overall acceptance.

## 6. Acceptance and anti-overfit checks

1. No-prompt operator open succeeds for two separately generated workbook paths/layouts and after close/reopen; missing/closed/other Excel cases cannot return another workbook's data. Direct parser actually fails on protected file; normal unencrypted control reads. Original bytes unchanged during task/Replay. Human-visible open and headless COM checks are recorded separately.
2. P0 target starts absent in the user's prepared venv; request requirements installation -> actual failure -> remote-origin exact Skill match -> explicit execution authorization -> actual install/version/import -> local +1 -> usage sync. Same run/event repeated adds zero. No runtime workspace substitution.
3. Varied directory names, local source aliases, package/version fixtures in automated checks, no matching Skill, unrelated errors and unavailable sources cannot force MATCH or reuse. Supported scope remains explicit rather than claiming arbitrary corporate packages.
4. Live branch before P1 contains P0 only. P1 actual search yields NO_MATCH for file-access, user supplies the environment fact, Agent investigates and creates environment-only candidate. Cold reuse stays zero. Filename/layout/values are not supplied as the answer.
5. Candidate exact ref/content is presented once for real human confirmation; changed digest, missing approval, Replay FAIL/NOT_RUN or push failure prevents PUBLISHED. No copied old P1 review/Replay even if the newly discovered content has the same digest.
6. After user publication, fresh receiver sees P0 + P1 on the same selected branch; first valid reuse event import +1, repeat +0. Verify organization vs local usage and initial vs final revision. Live final publication remains USER_PENDING until actually performed.
7. User transcript receives a July-only factual answer for July lookup and no false software-detection evidence. Investigative outcome is not scored by reproducing a fixed script; full expanded visible tool results, user prompts and state transitions are retained, excluding private reasoning and secrets.

## 7. Rules / readiness / review

Part 1 complete, Part 2 not started. Official rule files unchanged. Security/Resiliency extensions remain opt-out; existing NFR-SEC/NFR-RES still apply. Partial PBT-02/03/07/08/09 remain enabled for relevant pure/serialization invariants; execution and counterexample evidence belongs to implementation, not this plan. No new planning-stage PBT blocking finding. No diagrams or executable embedded payloads in this Markdown.

Remaining technical risks are real no-prompt Excel reopening and the limited pip Replay/gate extension; neither is already proven. Remote branch changes, initial P0 human review and final P1 human review are distinct from code-plan approval. Initial P0 review may be done during operator setup after its exact descriptor is prepared; final P1 review occurs during the user's Cold demonstration.

Review decision: approve the bounded impact decisions and steps 1–9, or request changes. This approval does not authorize erasure of existing shared history, fake success, automatic candidate approval or publication of P1 before the user demonstration.

[Answer]: Pending — user requested the plan first.

## Actual approval and bounded UX amendment

2026-09-09T02:05:26.8722098Z — User: 어 ai-dlc 과정을 충실히 이행하면서 진행해봐. github을 통해 시연할수있게. 그리고 p1시나리오 마지막에 사용자가 직접 게시하기 이렇게 요청하지않고, 권한 승인받는거처럼 요청이 오게끔 하는거로 변경해줘

Steps1–9 approved. Part2 starts now. Keep direct NASCA demo presentation. Accept feedback on verified setup, clear current state, actual-vs-reported evidence and non-expert UX; do not adopt reviewer score as fact or expand into a generic learning engine. Candidate completion automatically invites exact human review/publication via an operator permission prompt, without needing a separate publish utterance. Native operator confirmation is allowed; Agent cannot click/answer on behalf of the person. Implement a native review prompt in skillloop/review_prompt.py, preserving exact identity, fresh Replay and successful remote push. Plan approval remains distinct from candidate review.


## Approved correction — conversational approval
2026-09-09T02:11:28.7147405Z: User rejects Windows GUI; approval must be requested in Claude Code CLI conversation. Supersedes native review_prompt.py/--prompt plan. Remove unshipped GUI implementation. C9 displays current candidate and asks via Claude Code question UI; explicit answer is passed with exact digest and source text to review CLI. S3 rechecks current candidate identity and records the actual response/source. No standalone publish utterance, digest transcription or OS dialog. Receipt is supplied by the authorized Agent after user response, not cryptographic proof of a person. Existing terminal review retained. All other plan steps remain.


## Implementation validation receipt

165 passed/2 skipped in final full regression (seed20260909); skipped interactive Excel and obsolete unlinked-runner condition are explicit. Separate real Excel open2/2 and Git-backed P0 preflight pass. Setup follow-up15PASS covers final operator launcher/help behavior. Native GUI implementation removed per user correction, conversation receipt validates exact candidate and source response. New live branch75b6e54225a9fa4e71e7174168161d61fa923e31 has P0-only; all three user stores P1 count0/events0. Final live P1 approval/publication remains USER_PENDING. Full earlier failure and stale-store test failure retained.

Remote implementation receipt: 5fff0c4 pushed to origin/main. All nine implementation/preparation steps complete; final live P1 candidate permission/publication belongs to the user and is not marked PASS by this plan.

## Approved capture UX amendment — 2026-09-09T02:28:03.8177395Z
User explicitly requests removing connected status labels '팀 동기화 확인', '로컬 1개', '팀 게시 기준', redundant storage installation questions, and communicating reuse value. Existing US-UI-1/FR-UI-3 and US-P0-1; no new feature or storage/execution authorization change.
1. [x] C11 connected status: four lines with organization counts/contributions/ranking and last sync; hide duplicate local accounting. Unconnected diagnostics remain. Zero-reuse stored Skills are not popular Skills; use published organization ranking for connected stored list.
2. [x] C9 and CLI: already-configured storage used directly; no install/reconnect question. Exact remote execution confirmation, when required, asks about applying the displayed solution, not installing storage. Verified counted success explains reusing team knowledge and actual +1; no success claim before verification.
3. [x] Focused status/accounting and actual P0 regression; refresh prepared workspace C9 instructions, preserve data, record evidence, commit/push. No website edits or live-work resets.
Approval: latest user '얼른 수정해줘봐' plus specific requested text; bounded amendment proceeds under existing approved plan. P1 candidate approval remains separate.

Validation: initial focused run 37 passed/1 stale-display assertion failure (P0 14 tests passed). After aligning only requested text assertions, display/accounting rerun 24 passed. Three intermediate stale-text failures retained. No runtime behavior changed during assertion corrections. Prepared C9 copies refreshed; live status observed; no user-work counters reset.

## Approved P1 conversation wording amendment — 2026-09-09T02:55:22.8343603Z
User requests replacing the first failure follow-up with 'Agent SkillLoop를 통해 방법을 탐색해볼까요?' instead of asking how the file is normally opened. Bounded C9 presentation change: actual direct failure + actual NO_MATCH first, invite exploration and wait for response; do not supply Excel/COM as the answer. User may provide environment facts directly; do not ask an additional yes/no question after such a response. Neither exploration consent nor environment facts constitute candidate publication approval. P0 automatic reuse policy unchanged.
1. [x] Align all three C9 first-response instructions, superseding 'question-free stop' and former environment-question wording.
2. [x] Refresh existing P1 workspace Skill copies only; validate text consistency; preserve data and approval gates. Record user-reported P0 automatic run separately from independent tests. Provide existing operator fresh-Cold command, no destructive reset.
Approval: current explicit user request; proceed within existing CONSTRUCTION plan, no new component/functionality.

Validation: three first-response rules consistent; previous prompt absent; existing P1 copies refreshed. Instruction-only correction, no new runtime tests. Live Agent wording awaits user run.
