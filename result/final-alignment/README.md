# Final presentation alignment — execution evidence

Approved before implementation: aidlc-docs/construction/plans/final-presentation-alignment-plan.md. Product base75ef7e0; web source49c1711, revised webbe3013f. This validation changes U3 read-only presentation and the existing web explanation; P0/P1 execution lifecycle and exact shared descriptor are unchanged.

## Product checks

- U3/usage affected tests:44 PASS. Receiver import/repeat, exact reference/version/digest, duplicate event, unpublished candidate exclusion, local+shared non-addition, unlinked state all covered.
- Recorded receiver snapshot: receiver-org-snapshot.json and receiver-status.txt. Actual published remote Skill and one verified received event. Team1/local0. Store/usage bytes unchanged. Original author `local` intentionally retained; no fabricated person attribution.
- First combined run:141 PASS/2 SKIP/1 FAIL (pytest-first-failure.txt). Broad old assertion rejected valid unknown Git-sync text. Correction asserts connected S3/publication0 and separately unknown sync; focused10 PASS. The first run also emitted an HTTPResponse finalizer warning on Python3.14. Kept as observed; not silently removed.
- Final fixed-seed full run: **142 PASS / 2 SKIP** in239.68s, pytest-final.txt; seed20260908; no warnings on this final run. Actual Excel tests remain separate opt-in and are not replaced by mocks.

## Web checks

- npm ci success; npm test6 PASS; tsc/Vite production build PASS, web-build.txt. Web dependency lock retained.
- Browser directly controlled at localhost: P0 all4/P1 all8 steps. Single ordinary initial request, agent continuation without extra recovery prompts; explicit human exact-review and remote-execution confirmation retained.
- Candidate/review/Replay do not increase published count. Push stage increments publication. Warm after confirmation produces explanation reuse1 and new candidate0. Back from Warm gives reuse0; reset gives0 throughout.
- Archived actual Cold1650/Warm2550 charts render. Console initially clipped large chart; display now fitted without altering PNG pixels.
- Screenshot/DOM files in this directory are evidence of the **web explanation**, not additional Agent/Excel executions. P0/P1 actual runs remain in result/p0-reproduction and result/p1-acceptance.
- Browser warning/error logs empty. No Firebase comments/captures were written. Mobile-specific layout was not tested.

## Source and deployment

Main includes team-hub subtree and the existing Pages workflow, preserving web author ancestry while excluding older root rules/audit. Pages checkout now uses triggering github.sha. Web original third-party notices/license are included. Public deployment/CI receipts will be appended after remote confirmation. S3/DB support remains a future adapter, not implemented here.

## Remaining human/environment check

Separate B-PC Warm/Git roundtrip remains NOT_RUN. No more repeated same-source Cold tests are required by this correction. Final submission/gallery approval is not assumed.
