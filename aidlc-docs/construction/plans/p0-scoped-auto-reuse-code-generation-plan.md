# P0 scoped Team Skill automatic reuse — approved correction

Recorded: 2026-09-09T02:46:36.6804055Z. Current phase: CONSTRUCTION / integration defect and approved policy correction.

## User decision and impact
User explicitly requests removing repeated P0 execution confirmation under the feedback's narrow same-task/trusted-Team conditions, while following AI-DLC. This is a bounded NFR-SEC-4 exception, not a cosmetic-only fix. Prior universal prohibition and approval history remain in audit; current Requirements, US-P0-1 AC-4 and Application Design are updated before implementation. P1 file-access execution confirmation and human candidate review / fresh Replay / successful push remain unchanged. No Units or components added, no website edits.

## Minimal design / Code Plan
C8 checks an operator-provided scoped_auto_apply policy, never C9-generated confirmation. Conditions: an actual package-supply failure and C5 MATCH; exact digest integrity; action/source-only pip procedure; non-DEMO exact reference pinned by operator; same requirements path and existing work Python; named approved local source; matching trusted remote and branch; S3 PUBLISHED remote evidence and reuse eligibility. The imported publication evidence is Git provenance from the operator-selected trusted branch, not independent cryptographic proof of another human's review. Pin only the known P0 descriptor whose initial human review/Replay/publication was already executed; importing other/new content does not silently grant trust. Version/digest changes require new authorization. No generic remote code, credentials, elevation, system Python or wider resource access is authorized.

1. [x] Amend NFR-SEC-4 / US-P0-1 and design traceability with this precise exception. User's current directive authorizes these decisions and implementation; no repeated approval request.
2. [x] cli.py: evaluate scope and S3 provenance before S1, after existing actual failure and matching. Reject malformed/untrusted scope; retain explicit confirmation fallback; preserve C3 verification-only counting. Display selected friendly title and continuing-install message after authorization.
3. [x] scripts/org_demo.py and prepare-org-demo.py: explicit operator-only authorize-p0 setup for existing work, and new P0 preparation generates scoped policy for verified known exact P0. Preserve all prior data/approvals; C9 only reads policy. No policy generation on ordinary sync.
4. [x] C9: approved bounded P0 proceeds without a question or --confirm-skill fabrication; unauthorized result still asks. P1 unchanged. Refresh existing prepared P0 instructions/policy (no package or counter reset).
5. [x] Tests: scope mismatches (remote/branch/digest/workspace/procedure/DEMO/provenance), real Git pull + actual cold pip install/version/import +1 without confirmation, same run retry +0; P1/review regression. Record all results and provide fresh operator setup command. Commit/push scope with existing other-session changes preserved.

[Answer]: Approved by latest user '위 피드백을 참고해서 p0 과정 변경을 ai-dlc 과정에 충실히 이행하면서 변경해줘'. Part 1 recorded before Part 2. This approval concerns execution policy, never fabricates a new candidate publication review. Relevant security/resilience requirements still apply; opted-out workflow extensions stay opted out.

## Validation receipt
Initial combined run:24 PASS/1 SKIP/1 failure (test fixture attempted mutation of frozen dataclass). Corrected fixture with dataclasses.replace; scope13/13 PASS. Actual generic-package Git transport/install without confirmation passed; actual GitHub P0 Cold import/install/version/import +1 and same-run retry +0 passed separately. P1 services/integrity/Replay24 PASS. Prior failure retained. No live verification events pushed. New Agent language/automatic activation still requires user conversational run; CLI automatic execution itself is actually verified.
