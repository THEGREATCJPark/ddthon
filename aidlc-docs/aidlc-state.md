# AI-DLC State Tracking

## Project Information
- **Project Name**: Agent SkillLoop (MVP)
- **Project Type**: Greenfield
- **Start Date**: 2026-09-08T14:45:14Z
- **Current Phase**: INCEPTION
- **Current Stage**: **CONSTRUCTION 진입 — Units Generation 승인됨(정정 3건 반영, 2026-09-08)**. 다음: U0 P0 필수 + U1 최소 Functional Design → NFR Requirements(minimal) → Code Plan. **정정**: (1) U3 소유자=**CJ**('여력' 폐기), UI·조직 집계는 승인된 **필수 범위**(P0 비블로킹 ≠ 선택 기능); **U2(B) Day2 대기 해제**(계약+게이트 충족 시 즉시 병행 착수). (2) **파일별 단일 수정자**: usage.py=CJ(카운트+공유 이벤트), cli.py=CJ, gitsync.py=B(전송; 검증·dedup은 usage.py=CJ), envharness_p0.py=CJ/envharness_p1.py=B('함수별 분담' 폐기); U3 집계·표현=읽기전용, C3 공유 이벤트 import=상태 변경(쓰기). (3) 계약 5 **비블로킹**으로 정정, U0 전체 완료 대기 없이 P0 최소 계약+로컬 저장·카운트·환경 인터페이스 확정 후 U0/U1 **병렬**. **코드 작성은 설계·Code Plan 승인 + 공통 기준 SHA·작업 경로 확인 후.**
- **(이전) Units Generation (minimal) — 산출물 생성 완료**: Unit 정의(U0 공통·계약·통합/CJ, U1 P0 재사용 실행/A 최호길, U2 P1 경험·후보화·게시/B 한석훈, U3 조직 집계·표현·재사용 이벤트 공유, Q1 독립 QA 횡단/C 윤여훈), 의존성·계약 동결(1~8, P0 최소셋=1·3·4)·착수 순서(17:30 P0 앵커)·스토리 매핑(7개 전부 배정). 산출물: `application-design/unit-of-work.md`, `unit-of-work-dependency.md`, `unit-of-work-story-map.md`, `plans/unit-of-work-plan.md`.
- **(이전) Application Design Request Changes(2건 계약 보완)**: (1) **C10 상태 조회 경로**: S3에 읽기전용 상태 조회 계약(`list_lifecycle_states`/`query_lifecycle_state`, `remote_publish_evidence`/`local_review_evidence`) 신설, C10은 이를 통해서만 상태 조회(추정·게이트 재구현 금지). (2) **재사용 이벤트 공유 자격 분리**: `export_shared_usage(scope=VERIFIED_REUSE)`로 Skill 게시 게이트(SHAREABLE)와 분리, C3가 검증·event_id dedup, `sync`→C3/C4.push_shared_usage 경로는 S3.publish와 독립(A게시→B import→B 검증 성공→B 공유→A 1회 반영). 의존성 매트릭스·다이어그램·텍스트대안(C4→C3, C10→S3, localhost HTTP)·"네트워크 서비스 없음" 범위·UI 프레임워크 단계 표기·채택 repo/branch vs 미정 로컬 경로 정합화. **Application Design 전체 승인·Units Generation은 재검토 후 결정**(REVIEW REQUIRED).

## Workspace State
- **Existing Code**: No (문서 및 AI-DLC 규칙 파일만 존재)
- **Programming Languages**: 미정 (요구사항/NFR 단계에서 결정)
- **Build System**: 미정
- **Project Structure**: Empty (application code 없음)
- **Reverse Engineering Needed**: No (Greenfield)
- **Workspace Root**: C:\Users\cik61\Desktop\ddthon-main

## Code Location Rules
- **Application Code**: Workspace root (NEVER in aidlc-docs/)
- **Documentation**: aidlc-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Extension Configuration
| Extension | Enabled | Mode / Note | Decided At |
|---|---|---|---|
| Security Baseline | No | 전체 강제 미적용(Q12=X). 단, 핵심 보안 요구(secret·원본 데이터 비공유, read-only 승인 접근, 입력/무결성 검증, 원격 Skill 자동 실행 금지)는 일반 요구사항(NFR-SEC-*)으로 유지 | Requirements Analysis |
| Resiliency Baseline | No | 전체 강제 미적용(Q13=B). 단, 중복 방지·충돌 처리·sync 실패·재시작 보존만 요구사항(NFR-RES-*)으로 유지 | Requirements Analysis |
| Property-Based Testing | Yes | **Partial** 모드(Q14=B) — 강제: PBT-02, PBT-03, PBT-07, PBT-08, PBT-09 (round-trip/invariant/generator/shrinking·reproducibility/framework). 그 외 advisory. 적용 대상: 직렬화 round-trip, digest·dedup 등 순수·불변 로직 | Requirements Analysis |

## Stage Progress
### 🔵 INCEPTION PHASE
- [x] Workspace Detection
- [x] Reverse Engineering — SKIP (N/A, Greenfield)
- [x] Requirements Analysis (승인됨)
- [x] Workflow Planning (승인됨)
- [x] User Stories — EXECUTE (minimal) — 승인됨 (stories.md/personas.md)
- [x] Application Design — EXECUTE — **승인됨**(2026-09-08). Request Changes 2건 반영 + S3→C3 제외 판단 사용자 동의.
- [x] Units Generation — EXECUTE (minimal) — **승인됨**(2026-09-08, 정정 3건 반영: U3=CJ·필수 범위, 파일별 단일 수정자, 계약5 비블로킹·P0 병렬)

### 🟢 CONSTRUCTION PHASE (진입, per-unit loop 시작: U0 P0 필수 → U1)
- [x] Functional Design — EXECUTE (per-unit) — **P0(U0 P0 필수 + U1) 승인됨(2026-09-08, 정합화 3건 반영: 카운트 쓰기=C3 단독, run_id=실행 식별, 허용 index는 descriptor.procedure 근거)**. U2/U3 Functional Design은 이후 별도.
- [x] NFR Requirements — EXECUTE (per-unit, minimal) — **P0 승인됨(2026-09-08)**: pytest+Hypothesis 채택·의존성 명시, "네트워크 미의존"=외부 인터넷 미의존, mock index 제공 방식은 Code Plan 구체화.
- [ ] NFR Requirements — EXECUTE (per-unit, minimal)
- [ ] NFR Design — SKIP
- [ ] Infrastructure Design — SKIP
- [ ] Code Generation — EXECUTE (per-unit) — **Part 1(Code Plan) 승인됨(2026-09-08)**. **Part 2**: S0 `8ccbfdc` → S6 스텁 `b0ee495` → CJ S2~S5+cli `986d1cc` → e2e 본문 `c811316` → **C-a/C-b(store.py) `ef03b3a`, C-d(usage.py+cli.py) `cfc62e9`** → **U1(P0) A 인계 통합·실제 검증 완료 `e07af72`(main)**. **A 인계**: 패치 2파일 sha256 동일 → 중복 미적용, 별도 통합 branch `integ/u1-p0-875c97e`에서 `git am` → `9dea075`(저작자 hogil 보존, match.py/reuse_service.py). CJ `e07af72`: e2e unskip + 실제 Windows 버그 수정(run-p0 출력 유니코드가 cp949 콘솔에서 UnicodeEncodeError로 카운트 직전 크래시 → `_ensure_utf8_stdout()` UTF-8 reconfigure). **실제 검증: pytest 42 passed / 0 skipped(회귀 없음) + 실제 run-p0 2회 reuse=1→2, usage.json counts=2·events 2건·seen_run_ids 2건·share-export 동작.** **P0 실제 재사용 루프 완료(파일 존재 아닌 실행 결과로 판정).** 병합: `integ/u1-p0-875c97e`(9dea075→e07af72)→main fast-forward. README/EVALUATION 로컬 변경 미커밋 보존. **B 대기 정합화**: "구현 SHA 대기"→"실제 계약 연결·검증 대기"(P0 SHA=e07af72). 잔여: U2(B) Code Plan, U3(CJ), Build and Test.
- [ ] Build and Test — EXECUTE

### 🟡 OPERATIONS PHASE
- [ ] Operations — PLACEHOLDER

## Execution Plan Summary
- **실행**: User Stories(minimal), Application Design, Units Generation, Functional Design(per-unit), NFR Requirements(per-unit, minimal), Code Generation, Build and Test
- **생략**: Reverse Engineering(N/A), NFR Design, Infrastructure Design, Operations(placeholder)
- **다음 단계**: 현재 Application Design REVIEW REQUIRED 유지. 사용자의 별도 Application Design 전체 승인 후에만 Units Generation 진행.
- **문서**: aidlc-docs/inception/plans/execution-plan.md

## 승인된 SKIP 경계 (Workflow Planning 승인 시 확정)
- **SKIP-BOUNDARY-1**: NFR Design 생략 ≠ 요구 면제. 승인된 핵심 보안(NFR-SEC-1~4)·무결성(digest, FR-SKILL-4)·복원력(NFR-RES-1~4)은 해당 Unit의 Functional Design과 테스트에 반드시 반영한다. **(범위 변경 확장)** UI·동기화 Unit: 읽기전용 경계(NFR-SEC-2)·secret/원본 비표시(NFR-SEC-1)·동일 집계와 실적/DEMO_SEED 구분(FR-UI-3)·공유 usage dedup(FR-USAGE-4, FR-ORG-3)도 설계·테스트에 반영.
- **SKIP-BOUNDARY-2**: Infrastructure Design 생략 ≠ Git 원격 동기화 축소. 채택된 원격 sync 요구(FR-SYNC-1, Q3=A + 범위 변경으로 team-skill-store branch 채택)는 유지되며 로컬 Git만으로 축소하지 않는다. 원격 clone/pull/push·무결성·CONFLICT·실패 보존 유지. 실제 branch·Git 경로·세부 운용은 미결정(설계 승인 + Units 담당 확정 후 초기 구현 준비).

## 범위 변경 이력 (Scope Changes)
- **SCOPE-CHANGE-1 (2026-09-08, 승인됨)**: UI 추가(상태줄 FR-UI-1 + 로컬 읽기전용 대시보드 FR-UI-2, 동일 집계 FR-UI-3) + 조직 집계(FR-ORG-1~5, FR-USAGE-4) + Git 공유 방식 변경(별도 private 저장소 전제 → 동일 저장소 `team-skill-store` branch, 로컬 DB 미전송 FR-SYNC-5). 근거·영향: `plans/change-impact-ui.md`. **과거 Q3=A("별도 private 저장소")·기존 승인 이력은 보존**하고 이번 변경으로 일반화. 표현 참고=ttt(상태줄, organization.html; 백엔드 중앙 API 미채택, 소스≠렌더링). export=SHAREABLE 유지(최초게시·재시도 가능), PUBLISHED=원격 push 성공 후에만.

## Notes
- **U2 공통 의존성 계약 — 승인·구현 진행(2026-09-08)**: 산출물 `construction/plans/u2-shared-dependency-contracts.md`(승인 조건·최소 Code Plan 포함). **이 승인은 CJ 공통 의존성 계약·구현에 한정 — B의 U2 전체 설계/Code Plan 승인 아님.**
  - **C-a/C-b 구현 완료(store.py, C2)**: lifecycle `save/load_lifecycle_state`·`list_lifecycle_records`(저장만·전이 미판단, 키=id/version/digest); descriptor `export_bundle(refs 허용목록·3자 digest 일치·content만)`/`import_bundle(digest 재계산·위조 거부·DEDUP/CONFLICT·content만·승인/Replay 미생성)`. **검증: 전체 26 passed / 8 skipped**(기존 19→26). commit/push·SHA 보고 진행.
  - **C-d 구현 완료(usage.py C3 + cli.py C8)**: 스키마 `{counts,seen_run_ids,events}`(하위호환); `compute_event_id`(결정적·재전송 dedup 키); `record_actual_reuse`가 counted=True & digest 있을 때만 이벤트 생성(카운트·run_id dedup 불변); `export_shared_usage`(VERIFIED_REUSE만)/`import_shared_usage(blob, local_ref_exists)`(재검증·event_id dedup·로컬 존재 확인, counts 미변경); exact 참조·reuser_alias는 호출자(cli, env `SKILLLOOP_ALIAS`) 제공; CLI `share-export`/`share-import` 추가. **역산 금지**(digest 없는 evidence는 이벤트 미생성). **검증: 전체 34 passed / 8 skipped**(26→34). commit/push·SHA 보고 진행.
  - **제공 순서(B)**: ①store.py(C-a+C-b, 완료) ②usage.py+cli.py(C-d, 완료) ③P1 A·B 조율(P0 독립, B·A 합의 대기).
- **A(U1) 인계 상태 — 통합·검증 완료(2026-09-08)**: A push 403 차단 → 패치 전달. 패치 2파일 sha256 동일(중복 미적용). 최신 main 기준 별도 통합 branch `integ/u1-p0-875c97e`에서 `git am` → `9dea075`(저작자 hogil 보존). CJ 통합 `e07af72`(e2e unskip + Windows UTF-8 출력 버그 수정) → main fast-forward. **실제 검증 완료: pytest 42 passed/0 skipped + run-p0 실제 2회 reuse=1→2.** V5~V8·V12(run-p0 e2e) **NOT_RUN → PASS.** P0 통합 SHA=`e07af72`(docs `7256272`)를 B에게 전달(B 대기="실제 계약 연결·검증 대기"로 정합화).
- **P0 CLI 사용 확인(2026-09-08)**: 사용자 직접 `python -m skillloop run-p0` 실행 → 실패 관찰→MATCH→reuse=3(counted=True). **변경·오류 없으면 P0 반복 테스트 중단.**
- **P1 환경 모델 승인(2026-09-08)**: 사용자 승인 = B의 **Office 암호화 합성 파일 + 열린 Excel read-only 접근 모델** + **P1 한정 Excel 의존성 예외** → A/B 전달. **독립 Replay·게시 게이트 유지.** "환경 모델 선택 대기"로 **되돌리지 않음** — A/B의 구체 계약·계획 반영·구현을 기다린다. (이전 "의존성 미설치 재현" 대안은 철회됨.)
- **U3(CJ) 최소 설계 준비(2026-09-08)**: 승인된 필수 범위(조직 집계 C10·상태줄 C11·읽기전용 대시보드 C12) 최소 Functional Design+NFR(minimal)+Code Plan 작성 → `construction/plans/u3-minimal-design.md`(REVIEW REQUIRED). CJ 단일 수정자(org_aggregator.py/statusline.py/dashboard.py + cli.py), B 파일 미수정 → P1과 독립 병렬. **열린 결정 2건 확정(2026-09-08)**: ①lifecycle 상태=**보류형** — `LifecycleView`(계약7 형태) provider에만 의존, 미연결 시 "상태 조회 미연결"(0·추정 금지), **실제 경로 store 직접 읽기 우회 금지**, 테스트는 계약7 형태 명시적 test 대역, B 제공 시 연결; 이 결정으로 나머지 U3 대기 안 함. ②대시보드=**stdlib http.server** 127.0.0.1·정의된 GET 경로만·파일 임의 노출 금지.
  - **U3 Code Plan 승인·구현·검증 완료(2026-09-08)**: 신규 `org_aggregator.py`(C10)·`statusline.py`(C11)·`dashboard.py`(C12) + `cli.py` `status`/`dashboard` 서브커맨드(P0와 동일 `.skillloop_demo/` 경로 연결). 정직성 기준 반영(게시=lifecycle만·미연결시 "확인 불가", 원격 게시=remote_publish_evidence 있을 때만, 로컬 vs 조직 구분, 실적/DEMO 구분). **검증: U3 단위 21 passed + 전체 63 passed(42→63, 회귀 없음); `skillloop status` 실데이터(reuse=3) 확인; 대시보드 실 HTTP(127.0.0.1) GET 200·정의외 404·POST 405·본문 정직성 확인.** **하단 상태줄 연결은 사용자 settings 필요 → 실제 확인 전이므로 연결완료 보고 안 함.** lifecycle/last_sync 실데이터·조직 시연=계약7·C4 연결 후 **NOT_RUN**.
- **Process/provenance 정합성 정정(제품 scope change 아님)**: 이 시점 이후 구현 기준은 현재 `ddthon`에서 본선 중 생성·승인된 Requirements/User Stories/Workflow Plan/Application Design 및 이후 승인될 Units/Functional Design/Code Plan과 현재 실제 실행 증거다. Application Design 전체 승인 대기 상태는 유지한다. UI는 사용자 승인 FR-UI/FR-ORG 자체를 근거로 유지한다.
- **외부 사전 구현 Reference 사용 중단**: `ttt`를 포함한 사전 구현의 검색/Fetch/Open/Read/비교/코드 복사/테스트 결과 참조를 중단한다. 필요 시 이유·범위를 먼저 제시하고 사용자 승인을 기다린다. 현재 산출물·실제 오류부터 조사하며 과거 외부 PASS/코드 구조를 본선 완료 근거로 사용하지 않는다. 과거 audit/chat/변경 검토 및 위 SCOPE-CHANGE-1의 참고 사실은 보존한다.
- **Audit timestamp correction**: 과거 일부 entry의 workflow 시작 timestamp 반복은 capture 오류이며 동일 시각의 이벤트를 뜻하지 않는다. 기존 entry는 수정하지 않고 correction note를 append한다. 이후 각 entry 작성 직전에 PowerShell `Get-Date`로 OS 현재 시각을 새로 취득해 UTC ISO 8601(`Z`)로 기록하고 고정 timestamp를 재사용하지 않는다. 취득 실패 시 `timestamp unavailable`로 표시한다.
- 사용자 제약: 팀 4명, 개발 시간 제한(9/8 오후 ~ 9/9 오후), Windows-native 목표.
- 통합 위험 회피: 공통 state/lifecycle을 여러 세션이 동시 수정하는 구조 지양 (Workflow Planning/Units 단계에서 반영).
- 평가 제출 요건: 실제 source + aidlc-docs 전체 + README + 동작 screenshots/result 보존. Inception 과확장 지양.
- seam (a)~(g)는 **후보**이며 Unit 수·담당자·상세 구조는 Application Design/Units Generation에서 확정. seam (g)=조직 집계 read-model + 재사용 이벤트 공유(VERIFIED_REUSE, 게시와 독립) + 표현 표면(상태줄/대시보드, 범위 변경).
- **Units Generation 참고 방향(확정 아님)**: "CJ 통합·공통부 / A·B 개발 / C 독립 QA 운영" 방향을 우선 참고하되 **4명을 4개 개발 Unit으로 고정하지 않는다.** 실제 Unit 경계·사람 배정은 Units Generation에서 계약을 근거로 결정.
- **Request Changes(2건) 처리 계약 요약**: (1) S3 읽기전용 상태 조회 계약 신설 → C10이 유일 경로로 상태 조회(추정·게이트 재구현 금지, 원격 게시본은 remote_publish_evidence/local_review_evidence 분리·수신 환경 승인/Replay 미생성). (2) 재사용 이벤트 공유 자격 VERIFIED_REUSE(정확한 Skill 참조+실제 성공 근거+비-DEMO)를 SHAREABLE 게시 게이트와 분리, C3 검증·event_id dedup, sync 경로는 S3.publish와 독립. 신규 Skill 게시 게이트는 유지. 반영 파일: components/component-methods/services/component-dependency/application-design/execution-plan.
