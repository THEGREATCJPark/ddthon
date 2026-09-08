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
- [ ] Functional Design — EXECUTE (per-unit, **U2**, minimal) — **작성 → CJ FD 검토(1차) → CJ 공통 의존성 확정(2차) 반영, 개정본 승인 대기(2026-09-08, 담당 B)**. `construction/u2-p1-git/functional-design/functional-design.md`. 파라미터: **D-1**(자체 lifecycle.json **철회** → CJ `store` 저장·로드 계약 제공[C-a 확정, 제공 ①], 상태 판단·변경 요청·읽기전용 조회는 S3 단독, exact id/version/digest 연결, 영속 연동 SHA 전 NOT_RUN)·D-2(gitsync=team-skill-store 전용 로컬 미러)·D-3(push 불가 시 PUBLISH_PENDING+NOT_RUN)·**D-4**(team-skill-store 최초 초기화=B). **CJ 공통 의존성 확정(2026-09-08 2차)**: **C-a/C-b/C-d 호출 계약 확정** — 제공 순서 **① lifecycle 저장+descriptor import/export, ② 공유 usage 이벤트**, 각 항목 검증 commit SHA 전달 예정. C-b: digest 검증·DEDUP/CONFLICT는 **store 처리**(U2 미구현), S3는 **공유 자격 판단한 정확한 후보만 export**. C-d: 저장·검증·dedup=CJ, **Git 전송·pull·last-sync 경계만 B**, **event_id 재발급 금지**. **C-c**(A match P1 검색+파일접근 적용·검증)는 **대기 유지**(미구현 검색 NO_MATCH 금지). **자체 저장·무결성·CONFLICT·NO_MATCH 우회 없음. CJ 공통 계약 승인 ≠ U2 전체 구현 승인.** U3 상태 조회 계약(#7) 제공 정의. Code Plan **미착수**. 관련: `nfr-requirements/nfr-requirements.md`(초안, 승인 대기), `coordination-blockers.md`. **원격 push 미완료(권한 403, NOT_RUN) — 로컬 커밋만.**
- [x] NFR Requirements — EXECUTE (per-unit, minimal) — **P0 승인됨(2026-09-08)**: pytest+Hypothesis 채택·의존성 명시, "네트워크 미의존"=외부 인터넷 미의존, mock index 제공 방식은 Code Plan 구체화.
- [ ] NFR Requirements — EXECUTE (per-unit, minimal)
- [ ] NFR Design — SKIP
- [ ] Infrastructure Design — SKIP
- [ ] Code Generation — EXECUTE (per-unit) — **Part 1(Code Plan) 승인됨(2026-09-08)**. **Part 2 진행 중**: S0 기준커밋 `8ccbfdc` → S1 스텁 → S6 스텁 push `b0ee495`(=공통 기준) → **CJ S2~S5+cli 구현·push `986d1cc`(19 PASS)** → **e2e 본문·실행 준비 `c811316`**. **차단(A 대기)**: S7/S8(A 소유 match.py/reuse_service.py) 미구현 → V5~V8·V12(run-p0 e2e) **NOT_RUN**. run-p0는 failing index 실제 pip 실패 관찰까지 동작, match.search(A)에서 정지. cli.run_p0(run_id) 재시도 파라미터 추가. e2e(`test_run_p0_e2e.py`, CJ 단일 수정자) 본문 완료·**SKIP 유지**(파일 존재≠완료, 실제 설치·검증·카운트 확인 필요). **19 PASS / 8 SKIP 부분 검증 유지.** 수신 후 절차: `construction/plans/p0-integration-readiness.md`.
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
- **Process/provenance 정합성 정정(제품 scope change 아님)**: 이 시점 이후 구현 기준은 현재 `ddthon`에서 본선 중 생성·승인된 Requirements/User Stories/Workflow Plan/Application Design 및 이후 승인될 Units/Functional Design/Code Plan과 현재 실제 실행 증거다. Application Design 전체 승인 대기 상태는 유지한다. UI는 사용자 승인 FR-UI/FR-ORG 자체를 근거로 유지한다.
- **외부 사전 구현 Reference 사용 중단**: `ttt`를 포함한 사전 구현의 검색/Fetch/Open/Read/비교/코드 복사/테스트 결과 참조를 중단한다. 필요 시 이유·범위를 먼저 제시하고 사용자 승인을 기다린다. 현재 산출물·실제 오류부터 조사하며 과거 외부 PASS/코드 구조를 본선 완료 근거로 사용하지 않는다. 과거 audit/chat/변경 검토 및 위 SCOPE-CHANGE-1의 참고 사실은 보존한다.
- **Audit timestamp correction**: 과거 일부 entry의 workflow 시작 timestamp 반복은 capture 오류이며 동일 시각의 이벤트를 뜻하지 않는다. 기존 entry는 수정하지 않고 correction note를 append한다. 이후 각 entry 작성 직전에 PowerShell `Get-Date`로 OS 현재 시각을 새로 취득해 UTC ISO 8601(`Z`)로 기록하고 고정 timestamp를 재사용하지 않는다. 취득 실패 시 `timestamp unavailable`로 표시한다.
- 사용자 제약: 팀 4명, 개발 시간 제한(9/8 오후 ~ 9/9 오후), Windows-native 목표.
- 통합 위험 회피: 공통 state/lifecycle을 여러 세션이 동시 수정하는 구조 지양 (Workflow Planning/Units 단계에서 반영).
- 평가 제출 요건: 실제 source + aidlc-docs 전체 + README + 동작 screenshots/result 보존. Inception 과확장 지양.
- seam (a)~(g)는 **후보**이며 Unit 수·담당자·상세 구조는 Application Design/Units Generation에서 확정. seam (g)=조직 집계 read-model + 재사용 이벤트 공유(VERIFIED_REUSE, 게시와 독립) + 표현 표면(상태줄/대시보드, 범위 변경).
- **Units Generation 참고 방향(확정 아님)**: "CJ 통합·공통부 / A·B 개발 / C 독립 QA 운영" 방향을 우선 참고하되 **4명을 4개 개발 Unit으로 고정하지 않는다.** 실제 Unit 경계·사람 배정은 Units Generation에서 계약을 근거로 결정.
- **Request Changes(2건) 처리 계약 요약**: (1) S3 읽기전용 상태 조회 계약 신설 → C10이 유일 경로로 상태 조회(추정·게이트 재구현 금지, 원격 게시본은 remote_publish_evidence/local_review_evidence 분리·수신 환경 승인/Replay 미생성). (2) 재사용 이벤트 공유 자격 VERIFIED_REUSE(정확한 Skill 참조+실제 성공 근거+비-DEMO)를 SHAREABLE 게시 게이트와 분리, C3 검증·event_id dedup, sync 경로는 S3.publish와 독립. 신규 Skill 게시 게이트는 유지. 반영 파일: components/component-methods/services/component-dependency/application-design/execution-plan.
