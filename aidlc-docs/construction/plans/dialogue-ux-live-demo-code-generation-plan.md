# C9 대화·도구 안내 정합화와 실제 P0 UI 시연 — Code Plan

상태: **Part 2 수정·회귀 완료 / 실제 P1 2-turn PASS / P0 LIVE UI NOT_RUN / 원격 CI/Pages 확인 완료**.
기준: main `8bd731b4f3c085577604712bc3783117abfcd426`. 시작 작업 트리 clean, origin/main 일치. 기존 CONSTRUCTION / 통합 Build & Test에서 발견한 결함의 보완이다. Inception과 기존 승인을 재시작하지 않는다.

## 1. 요청과 승인 경계

사용자가 첨부 프롬프트의 실행을 요청했으며, 그 프롬프트 §0에서 최소 Code Plan 작성과 승인 gate를 명시했다. 이번 기록은 요청 접수·영향 분석·실행 계획이며 **이 새 계획의 승인이나 구현 완료를 소급 기록하지 않는다**. 구현·검증·UI 실행·제출 표현·push/deploy를 포함한 아래 순서를 한 번 승인받은 뒤 진행한다. 기존 환경 모델/기술/후보 lifecycle은 재질문하지 않는다.

근거 규칙: `.aidlc-rule-details/construction/code-generation.md` Part 1 Step 7, `common/workflow-changes.md`, `construction/build-and-test.md`.
현재 파일 소유: aidlc-state의 최신 A/B 인수 완료 기록에 따라 CJ가 통합 소유. A/B 원격 최종 SHA는 각각 cb25a62/1760d32이며 새 원격 이동 없음. 로컬 clean과 기존 인계 기록을 확인했지만 타 PC 프로세스까지 관찰했다고 주장하지 않는다. 이후 새 변경 발견 시 해당 파일만 조율한다.

## 2. 기존 산출물과 실제 코드의 대조

| 항목 | 확인 결과와 조치 | 추적성 |
| --- | --- | --- |
| P0 자연어 요청 | apply-requirements가 실제 공급 시도·관찰·C5·S1·C3를 같은 작업 Python에서 수행. 별도 match나 run-p0로 대체할 필요 없음 | US-P0-1, FR-P0/FR-SURF/FR-USAGE |
| 카운트 시점 | S1의 설치·버전·별도 프로세스 import 검증 후 C3 기록. 이후 Agent 재확인은 추가 수용 증거이며 별도 신규 카운트 게이트가 아님. 기존 실적 경로 유지 | US-P0-1 AC-3/5, p0-nl/p0-repro 계획 |
| P1 사용자 환경 사실 | FR-P1-3와 US-P1-2 AC-1에 대화형 환경 확인이 이미 있음. 현재 C9가 NO_MATCH 뒤 곧바로 탐색하므로 빠진 사용자 턴 복원 | FR-P1-3/4, US-P1-1/2 |
| P1 도구 계약 | task_rows는 정확한 네 key, 양의 정수, worksheet 절대 좌표를 이미 검사함. --help에는 세부 계약 부족. 계약 설명을 보강하며 정답 배치 미제공 | p1-scenario-correction-plan, FR-P1-5/6 |
| Org Knowledge | 현재 execute_p1은 Team Skill store만 검색하며 별도 조직 지식 입력/검색 adapter 없음. 실제 trace에 scope/query/result와 `not_provided`를 명시. '제공된 Org Knowledge'의 조건부 의무는 삭제하지 않음 | FR-P1-2, US-P1-1 AC-2 |
| Replay | 새 접근·원본 불변·exact digest 검증은 구현. 별도 PC/Agent/문서를 언제나 강제하는 코드가 아님. 다른 workbook의 과거 실제 증거는 그대로 유효한 과거 증거 | FR-P1-7, result/p1-acceptance |
| OLS | verify_work_result는 동일 계산 함수 기반 self-check. 별도 expected 값의 기존 acceptance 및 순수 함수 테스트가 있음. 새 oracle 프레임워크 불필요 | FR-P1-5, 기존 acceptance |
| DEMO_SEED 20 | FR-USAGE-3은 데모/실적 구분을 유지하나 현재 준비 도구 usage는 빈 counts이고 활성 20 baseline 없음. 20을 다시 만들지 않고 웹 실제 검증 설명 0→1 사용 | FR-USAGE-3, tests/prepare_p0_work.py |
| 웹 팀 Skill 수 | 현재 demoCounts.published는 이번 신규 게시만 세어 P0에서도 0. 기존 사용 가능 Skill과 이번 신규 게시를 분리. 로컬 승인 Skill을 원격 Published로 바꾸어 말하지 않음 | 승인 final-presentation-alignment-plan |
| GUI 도구 | computer-use SKILL.md/guidance/API/confirmation을 읽고 @oai/sky 초기화·실제 앱 목록 호출 성공. 현재 Claude UI 실행창은 없음. 실제 시연은 미실행 | 요청 §11~14 |

이번 수정은 새로운 요구사항/Unit/DB/어댑터를 추가하지 않는다. Org Knowledge가 실제로 제공됐는데 미검색하는 경우에는 `not_provided`로 위장하지 않고 미지원/미검증으로 보고한다. Requirements 의미 변경이 필요해지는 경우 해당 한 건만 별도 change gate로 올린다.

## 3. 최소 설계·NFR

- C9는 한국어 요청에 짧은 한국어 업무 설명을 유지한다. 내부 진단 원문은 로그에 보존하고 기본 답변에는 결과·필요한 한계·실제 chart 경로만 전달한다. 고정 성공 대본이나 특정 Skill/열/값을 주입하지 않는다.
- P1 첫 요청 → 실제 직접 실패·Team Skill NO_MATCH → 환경 사실 질문에서 턴을 끝낸다. 사용자 메시지로 Excel 열람 사실이 제공된 뒤 환경 탐색한다. 이미 사용자 대화에 그 사실이 있으면 중복 질문하지 않는다. workspace metadata나 잠금 파일은 사용자 답변/실제 attach 성공과 동일하지 않다.
- `--app-open`은 보고된 전제이며 실제 대상 workbook 접근 성공은 어댑터 근거로 판단한다. 잠금 파일·OLE header만으로 앱 열림/암호화/실제 NASCA 원인을 확정하지 않는다. 표시 `사내환경 · NASCA(가상)`은 제공된 환경 설명으로 유지한다.
- task-mapping 계약은 `sheet` 문자열, `month_col`/`total_col`/`first_row`는 1-based 양의 정수, worksheet 절대 좌표, 서로 다른 두 열. 현재 문서에서 Agent가 실제 값을 판단한다.
- 기존 candidate procedure/digest, 사람 review, fresh Replay, remote 확인 후 PUBLISHED, 실패 PUBLISH_PENDING, 원격 Skill 실행 확인을 유지한다. 업무 값·암호·시트·열·차트는 공유하지 않는다.
- Partial PBT-02/03/07/08/09 유지, seed 기록. Security/Resiliency 확장 opt-out 유지(재질문 없음), 기존 NFR-SEC/NFR-RES는 적용. 새 infra/framework/performance 목표 없음.

## 4. Code Generation Part 2 — 승인 후 순서

- [x] 1. `.claude/skills/skillloop/SKILL.md`: 한국어·업무 중심 설명, P1 사용자 환경 사실 턴, 관찰과 추정 구분, task-mapping 계약, 최종 실제 chart_ref 링크. 기존 P0/C3/승인 경로는 보존. 기존 `--policy` 지원과 일치하는 범위 설명으로 정합화하고 범용 지원 주장은 하지 않는다.
- [x] 2. `skillloop/cli.py`: run-p1 도움말의 정확한 JSON key/type/절대 좌표와 정상 대기 상태 안내. `skillloop/experience_service.py`: search trace에 실제 Team Skill scope/query/result와 Org Knowledge 미제공을 명시하고, facts_needed에 환경 사실 확인을 안내. candidate/계산/게이트/적용 선택 로직은 변경하지 않는다. `envharness_p1.py`/`replay.py`는 이번에 읽기 검토만, 결함 없는 실행 코드를 재작성하지 않는다.
- [x] 3. `tests/test_p1_services.py`, 필요시 `tests/test_cli_match.py` 또는 신규 `tests/test_cli_p1_help.py`: NO_MATCH 대기 시 reader 미호출·후보/usage 무변경, 실제 검색 scope, 도움말 필수 계약 검사. 기존 mapping/digest/OLS/approval 테스트 재사용. 문구 전체 일치나 강제 Agent 성공 대사 테스트는 만들지 않는다.
- [x] 4. `team-hub/src/demoScenarios.ts`, `Demo.tsx`, `demoScenarios.test.ts` 및 필요한 기존 CSS: P0 4단계 유지, P1 NO_MATCH 이후 사용자 환경 사실 턴 추가; Cold 차트/후보/사람 검토/Replay/게시/새 Agent Warm 보존. 기존 사용 가능 Skill·이번 신규 게시·실제 검증 0→1을 구분. 20 baseline 신설 없음. 설명용 시뮬레이션·보관 실제 차트·증거 링크 유지. Firebase 커뮤니티 동작 변경 없음.
- [x] 5. 변경 경로 targeted 회귀 후 Python 전체/PBT seed20260908, web tests/production build. 기존 테스트 개수를 목표로 수정하지 않는다. P0 retry +0는 기존 실환경/단위 검사로 확인. P1은 새 독립 작업공간에서 **한 번의 2-turn Cold**를 실제 실행: 첫 자연어 업무 요청 → 관찰·검색·환경 질문 → 제공된 두 번째 사용자 문장 → 탐색·다른 layout·업무·차트·후보1/reuse0. 테스트 운영자가 두 번째 문장을 넣는 경우 operator-assisted test라고 명시하고 실제 사용자가 입력했다고 하지 않는다. 원본 해시와 별도 expected값 대조. 새 후보를 자동 승인/게시하지 않는다.
- [ ] 6. 제품 소스를 commit하여 SHA 고정 후 **P0 LIVE DEMO RUN #1**: 새 isolated work venv/기존 승인 Skill/시작 usage 기록, 실제 Claude Code interactive UI에 사용자 업무 문장 한 번만 Computer Use로 입력. headless 대체 금지. 동일 세션에서 요청/실패·검색/성공·상태줄 캡처, 중간 오류 보존. 사전 준비는 기존 도구로 하고 UI에는 셸 명령 대신 Claude 업무 요청만 입력. 정상적인 권한 확인은 현재 허용 범위 내에서 처리하고 환경 파손 시 추가 성공 세션을 임의 생성하지 않는다.
- [x] 7. `result/dialogue-ux-20260909/`에 targeted/full/web/2-turn Cold 증거. `result/live-demo-p0-20260909/`에 README, run-context.json, verification.json, visible-transcript.md, 실제로 취득한 01/02/03 PNG와 가능한 대표 00 PNG. private reasoning/secret 제외. UI 불가 시 정확한 원인의 NOT_RUN과 사용자 3~4단계만 남기고 가짜 파일 미생성. 실제 성공/캡처가 있을 때만 웹에 별도 실제 P0 증거 카드 연결.
- [x] 8. `README.md`, `aidlc-docs/aidlc-state.md`, `construction/build-and-test/build-and-test-summary.md`, 본 계획 상태, audit append-only 정합화. 기존 파이프라인으로 push/deploy, 최종 제품/web exact SHA의 CI/Pages와 public 브라우저 확인. 문서·증거 후속 SHA와 검증 제품 SHA를 구분. B-PC 미준비는 NOT_RUN 유지. 요청한 12항목 결과 형식으로 보고.

## 5. 재사용 가능한 증거와 새 증거

기존 142 PASS/2 SKIP은 이전 코드의 회귀 기준이다. 이번 최종 소스의 PASS로 바꿔 부르지 않는다. 과거 P0/P1 Cold 로그의 영어·입력 오류·실패는 보존한다.

후보 content/digest와 lifecycle 코드를 변경하지 않는 이 계획에서는 기존 exact 사람 승인/다른-workbook Replay/GitHub 게시·Warm 증거를 **기존 게시 Skill의 이력**으로 참조한다. 새 Cold 로컬 후보가 같은 digest라는 이유만으로 로컬 승인·Replay를 새로 생성하거나 승계하지 않는다. 이번 P1 UX 2-turn과 P0 interactive 실행은 별도 근거로 저장한다. 다른 PC 강제/실제 B-PC/새 원격 왕복을 완료했다고 확대하지 않는다.

## 6. 계획 검토

위 8단계 전체(최소 수정 → 회귀 → P1 2-turn → 실제 P0 UI 1회 → 증거·웹 연결·CI/Pages)를 승인받은 후 구현한다. 기존 확정 기술·담당·lifecycle에 대한 추가 질문은 없다.

[Answer]: 어 승인 (실제 승인 기록은 아래 절 참조)

## Actual approval / Part 2 started

2026-09-09T00:15:59.7512103Z — User (raw): 어 승인. Eight-step plan approved before code changes. Earlier review text is preserved as history.


## Execution receipt (local)

Steps1–5 and7 complete. Step6 attempted preparation/launch only: actual UI prompt and capture NOT_RUN due target not exposed. User fallback guide provided; not marked as successful execution. Step8 final remote verification underway. Minor narrative limitations are documented; no new candidate human approval.


## Final remote receipt

Python CI success at 9065a72284d93eb2fffdda51401f34638457e681 (run34295654337). Pages success at6fefa6bbfd3c2614771a81e9c7d5aba0ab19187a (run34295561705). Current Python tree equals testedfff0ffa; current web source tree equals deployed6fefa6b. Public browser confirmed index-Da_E1P2H.js and the user environment-fact turn. Initial cached response used the previous bundle; cache-distinct navigation verified the current bundle. Local full flow evidence is retained. Step8 complete; Step6 remains NOT_RUN, not waived or passed. Overall final acceptance and B-PC remain pending.

## P0 live feedback amendment — bounded presentation correction

User requested natural observed-error guidance, visible preloaded Skills at zero reuse, and a named verified-success message. This is a Request Changes within existing C9/C11/CLI presentation scope; current request authorizes the corrections. It is not approval to invent proxy/timeout failures, historical success events or PUBLISHED evidence. No website changes.

- [x] C9: explain observed package-not-found in ordinary Korean, announce search intent; report selected display name and actual counted delta only. Do not infer blocking/timeout from package-not-found.
- [x] C11: show local stored Skill title even at zero reuse; label it stored rather than popular. Distinguish local storage from verified remote publication and no success from no Skill. Keep four lines, readonly state and terminal-label sanitization.
- [x] CLI: reuse the presentation title lookup and emit success wording only after S1 success and C3 counted=True. Explicit no-addition wording when not counted. No digest/content/approval changes.
- [x] Validate zero-use inventory, empty inventory, real popularity, counts/readonly and real install/repeat-no-reuse messages; run relevant regression. Copy only updated Skill instructions to the known P0 work folder, preserve settings/store/usage and original live result.
- [x] Record actual validation and user-report vs locally-read usage evidence, commit/push product/docs only. Remote Skill preload/publication remains a separate transport scenario; no remote data mutation.

Current local evidence: user-provided prompt/early pip error is incomplete as a full transcript. Work usage contains one verified event at2026-09-09T00:54:57Z; that is recorded evidence, not an observed full UI capture. Existing NOT_RUN receipt for the earlier automation attempt remains historical.

Validation receipt: targeted37 PASS, P1 services10 PASS, final real P0 repeat1 PASS with inherited PYTHONUTF8=1. Initial parent-only UTF-8 run passed with2 reader warnings, preserved separately. Known P0 work C9 refreshed, protected settings/store/usage unchanged. New skillloop-p0-feedback-20260909 work venv is PREPARED_NOT_RUN and points to existing actual local history1; no new event created. Latest dialogue phrasing is not yet independently validated in a fresh Agent session. Web and remote data unchanged.
