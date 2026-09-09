# Application Design (통합) — Agent SkillLoop

**단계**: INCEPTION / Application Design — Part 2
**작성일**: 2026-09-08
**근거**: 승인된 `requirements.md`, `stories.md`/`personas.md`, `application-design-plan.md`(AD-Q1~Q6 승인)

> 이 문서는 `components.md` · `component-methods.md` · `services.md` · `component-dependency.md`를 **통합 요약**한다. 컴포넌트·서비스는 **책임 축 기반 분석·제안**이며, **개수·경계·사람 배정은 확정이 아니다**(Units Generation에서 결정). 상세 비즈니스 규칙은 **Functional Design(per-unit)**.

---

## 1. 설계 원칙 (승인된 결정 반영)

- **AD-Q1 책임 축 도출**: seam (a)~(f)에 일대일 대응하지 않음. 함께 변경되는 공통 lifecycle은 과도하게 쪼개지 않음.
- **AD-Q2 identity↔usage 인터페이스 분리**: 불변 content(digest 대상)와 가변 usage(카운트)의 조회·변경 책임 분리. **usage 변경은 digest 불변**. 별도 DB·실행 서비스는 불필요.
- **AD-Q3 전용 게시 파이프라인(S3)**: 검토·독립 Replay·게시·상태 전이를 한곳에서. CLI·sync가 게이트 우회 금지. 내부 논리 서비스.
- **AD-Q4 store 위 sync**: GitSyncAdapter=전송, SkillStore=무결성·CONFLICT·dedup·저장. sync는 파일 직접 수정·게시 lifecycle 구현 금지. 원격 상태 문자열만으로 검증 인정 금지.
- **AD-Q5 명시적 계약 + 소유 컴포넌트만 쓰기**: Python 내부 호출, 타 상태 직접 수정 금지, 실제 성공 식별로 retry/sync/restart 중복 집계 방지. 네트워크 서비스·브로커 미도입.
- **AD-Q6 얇은 CLI wrapper**: 핵심 로직은 CLI, Agent Skill은 자연어→CLI 연결만. 사람 단독 재현 가능.

---

### 1.1 설계 정합화 (Request Changes 반영 — 2026-09-08, 컴포넌트 수 불변)
- **EnvHarness↔Agent 분리**: EnvHarness는 **합성 환경 준비만**. 직접 접근 실패를 **강제 raise 하지 않고**(`attempt_direct_parse`로 실제 실행 관찰), **정답 대안 절차를 공급하지 않는다.** 환경 관찰·대안 선택·코드 작성·실행은 **실제 업무 Agent**의 역할이며 CLI(`run-p1`)로 연결된다. "얇은 wrapper"는 제품 로직 중복 금지이지 Agent 탐색 역할 제거가 아니다.
- **재사용 경로·검증 책임 분리**: S1 ReuseService는 **시나리오 비의존** — 매칭 Skill의 applicability(문제 유형)로 적용·검증 방식 결정(파일접근 Skill을 pip 흐름으로 처리하지 않음). **S1.verify()=Skill 직접 효과 검증**, **S2.verify_work_result()=요청 P1 업무 결과 검증(FR-P1-5)**. 재사용해도 업무 완료·검증까지 수행하며, 새 발견 없이 중복 후보를 만들지 않는다.
- **로컬 확정 ≠ 원격 게시 완료**: S3 상태에 `LOCALLY_APPROVED`/`PUBLISHED`/`PUBLISH_PENDING` 구분. push 성공 시에만 PUBLISHED, 실패 시 PUBLISH_PENDING(로컬 보존+재시도 근거). export 대상은 **SHAREABLE(정확한 후보 사람 승인 + 독립 Replay PASS + digest 동일성)** 기준 — "원격 전송 완료(PUBLISHED)"를 전제하지 않아 **최초 게시가 배제되는 순환 조건이 없다.** import는 원격 상태 문자열로 로컬 승인·Replay 기록을 생성하지 않는다.

### 1.2 범위 변경 반영 (UI + Git 공유, 2026-09-08 승인 — `plans/change-impact-ui.md`)
- **Git 공유 대상 채택**: sync 대상을 **동일 저장소 `THEGREATCJPark/ddthon`의 `team-skill-store` branch**(합성·비민감)로 채택(FR-SYNC-1 일반화, ASSUMPTION-1 갱신). `main`=제품·산출물·증거. **로컬 DB 파일은 Git 미전송**(FR-SYNC-5), descriptor + 비민감 재사용 이력만 공유. clone/pull/push·무결성·CONFLICT·실패 보존 불변. 과거 Q3=A "별도 private 저장소" 결정은 보존하고 이번 변경으로 일반화. **실제 branch·Git 경로·세부 운용은 미결정**(설계 승인 + Units 담당 확정 후 초기 구현 준비).
- **공유 usage 집계 계약 추가**: C3에 공유 재사용 이력 **export/import + 이벤트 id 검증·dedup**(FR-USAGE-4, 재동기화 중복 +1 금지). 조직 현황은 로컬 조회만으로 불가 → **집계 계약 필요**(FR-ORG-1~5: dedup/버전 구분 공유 Skill 수·작성자(origin)/재사용자(alias) 식별 및 팀원별 기여·다른 환경 실제 재사용 반영·로컬 vs 원격 공유 완료 구분·last-sync 메타).
- **재사용 이벤트 공유 자격 = Skill 게시 자격과 분리(Request Changes 반영)**: 재사용 이벤트 공유 자격 **VERIFIED_REUSE**(정확한 Skill 참조 + 실제 성공 근거 + 비-DEMO)는 **신규 Skill 게시 게이트(SHAREABLE)와 별개**다. import 한 남의 게시 Skill 을 **실제 재사용만** 한 환경도 재후보화·재승인·재Replay 없이 실적 이벤트를 공유한다(A게시→B import→B 검증 성공→B 이벤트 공유→A가 조직 실적에 1회 반영, C3가 검증·event_id dedup). **신규 Skill 게시 게이트는 그대로 유지.** 이 공유 경로(`sync`→C3/C4.push_shared_usage)는 **S3.publish 와 독립**.
- **UI 표면(읽기전용 파생)**: **C10 OrgAggregator**(두 화면 공용 단일 스냅샷, 소유 상태 미수정) → **C11 StatuslineRenderer**(FR-UI-1) / **C12 DashboardServer**(FR-UI-2, localhost 읽기전용). 두 화면 **동일 집계 기준**, 실제 실적/`DEMO_SEED` 구분(FR-UI-3, FR-USAGE-3). **C10의 후보/검토/Replay/게시 상태는 S3 읽기전용 조회 계약(`list_lifecycle_states`)으로만 조회**하고 추정·게이트 재구현을 하지 않는다(Request Changes 반영). 원격 게시본은 `remote_publish_evidence`/`local_review_evidence`를 분리 표시하며 수신 환경 승인·Replay 기록을 만들지 않는다(AD-Q4). UI의 현재 근거는 **사용자 승인 FR-UI/FR-ORG**이며 특정 외부 구현 코드·backend 구조에 의존하지 않는다. UI 프레임워크·표시 방식 미결정(해당 Unit NFR Requirements(minimal)→Code Generation).
- **"네트워크 서비스 없음" 범위 명확화**: 내부 컴포넌트 통신에 적용(브로커·상시서버·중앙 API 없음). **C12의 localhost(127.0.0.1) 읽기전용 HTTP 화면은 사람용 로컬 시연 표면(예외)**이며 내부 통신 수단·외부 노출이 아니다(NFR-SEC-2).
- **SHAREABLE 유지 + PUBLISHED 기준**: descriptor 게시 자격 SHAREABLE(승인+Replay PASS+digest 동일성)로 **최초 게시·실패 후 재시도 모두 가능**, **PUBLISHED는 원격 push 성공 확인 후에만** 표시.

## 2. 컴포넌트 (책임 축 — 개수 제안)

| ID | 컴포넌트 | 핵심 책임 |
|---|---|---|
| C1 | SkillDescriptor | 불변 content/가변 usage 논리 분리, digest(불변 content만) |
| C2 | SkillStore | 로컬 저장·dedup·무결성·CONFLICT·import/export·재시작 보존 |
| C3 | UsageTracker | 실제 성공만 카운트·중복 집계 방지·DEMO_SEED 구분 |
| C4 | GitSyncAdapter | Git 전송(store 계약 위). push_descriptors(SHAREABLE)/push_shared_usage(VERIFIED_REUSE)/pull. 대상=team-skill-store branch, 로컬 DB 미전송, last-sync 메타 |
| C5 | SkillSearchMatcher | 결정적 검색+applicability+근거, NO_MATCH 구분 |
| C6 | ReplayVerifier | 독립 Replay → 실제 PASS/FAIL/NOT_RUN |
| C7 | EnvHarness | 합성 환경(P0 이중 index, P1 보호 XLSX+허용 대안) |
| C8 | CLI | 핵심 명령, 서비스 위임, 게이트 비우회 |
| C9 | AgentSkillWrapper | 자연어→CLI 얇은 wrapper |
| C10 | OrgAggregator (범위 변경) | 읽기전용 조직 스냅샷 집계(dedup/버전·기여·상태·랭킹·last-sync) |
| C11 | StatuslineRenderer (범위 변경) | 스냅샷 → 상태줄 간단 표시 |
| C12 | DashboardServer (범위 변경) | 스냅샷 → localhost 읽기전용 대시보드 |

**서비스(오케스트레이션)**: S1 ReuseService(P0), S2 ExperienceService(P1 업무·후보화), S3 PublishPipeline(검토·Replay·게시 게이트).

> 상세 메서드 시그니처는 `component-methods.md`, 서비스 흐름은 `services.md`.

---

## 3. 의존성 요약

- 계층: **Surface(C8/C9) → Service(S1~S3) → Capability(C5/C6/C7)·Persistence(C2/C3) → Domain(C1)**. 순환 없음.
- **C4 → C2 / C4 → C3**: import/export 계약 위에서만(descriptor=C2, 공유 재사용 이벤트=C3, 검증·dedup은 C3). **S3만** 게시 상태 전이 소유 + **읽기전용 상태 조회 계약 제공**(C10이 이를 통해서만 상태 조회). **C3만** usage 쓰기·검증·dedup. **재사용 이벤트 공유(VERIFIED_REUSE) 경로는 S3.publish 와 독립.**
- 상세 매트릭스·다이어그램(Mermaid+텍스트 대안)·계약 우선 고정 지점은 `component-dependency.md`.

---

## 4. 스토리·요구사항 추적성

| 스토리 | 서비스/컴포넌트 | 핵심 요구사항 |
|---|---|---|
| US-P0-1 | S1 ← C5, C7, C2, C3, C8/C9 | FR-SURF, FR-P0, FR-MATCH, FR-USAGE, NFR-SEC-4 |
| US-P1-1 | S2 ← C5, C7 | FR-P1-1/2, FR-MATCH, NFR-SEC-2 |
| US-P1-2 | S2 ← C7, C1 | FR-P1-3/4/5, NFR-SEC-2 |
| US-P1-3 | S2 ← C1 | FR-P1-6, FR-SKILL, NFR-SEC-1/3, NFR-RES-1 |
| US-P1-4 | S3 ← C6, C2, C4.push_descriptors; 재사용 이벤트 공유=sync→C3(VERIFIED_REUSE)/C4.push_shared_usage(게시와 독립) | FR-P1-7, FR-SYNC-1~5, FR-USAGE-4, NFR-RES-2/3, NFR-SEC-4 |
| US-UI-1 | C11 ← C10 ← C2/C3/C4.last_sync + S3 상태 조회(읽기전용) | FR-UI-1/3, FR-ORG, FR-USAGE-3/4 |
| US-UI-2 | C12(localhost 읽기전용) ← C10 ← C2/C3/C4.last_sync + S3 상태 조회(읽기전용) | FR-UI-2/3, FR-ORG, FR-USAGE-3/4, NFR-SEC-1/2 |

---

## 5. SKIP-BOUNDARY 반영 확인 (Workflow Planning 승인 경계)

- **SKIP-BOUNDARY-1(NFR 핵심)**: 보안(NFR-SEC-1~4: 원격 자동실행 금지 C9/NFR-SEC-4, read-only C7, 무결성 C1/C2, 비공유 C1/S2), 무결성(digest C1/C2), 복원력(dedup C2, CONFLICT C2, sync 실패 보존 C4, 재시작 보존 C2/C3)이 **컴포넌트 책임으로 반영됨** → 각 Unit의 Functional Design·테스트에서 구체화.
- **SKIP-BOUNDARY-2(원격 sync 유지, 범위 변경 갱신)**: C4 GitSyncAdapter가 **Git 원격(team-skill-store branch)** push/pull 담당 — 로컬 Git만으로 축소하지 않음. 원격 clone/pull/push·무결성·CONFLICT·실패 보존 유지. UI 추가·Git 변경 포함해 **NFR Design·Infrastructure Design = SKIP 유지**(로컬 읽기전용 표시 + 동일 저장소 branch, 신규 인프라 없음). **NFR Requirements(minimal)**는 UI·동기화 Unit에도 적용(집계 일관성·공유 usage dedup·읽기전용 경계).

---

## 6. 설계 완전성·정합성 검증

- ✅ 7개 스토리(US-P0-1, US-P1-1~4, US-UI-1/2)·주요 FR/NFR 모두 컴포넌트/서비스에 매핑(위 §4).
- ✅ identity↔usage 분리, 게시 게이트 단일 소유, store 위 sync, 소유 컴포넌트만 쓰기, **집계·표현은 읽기전용 파생(무쓰기)** — 승인 결정과 정합.
- ✅ 범위 변경(UI+Git)은 승인됨. seam을 컴포넌트/Unit 수로 확정하지 않음. Unit 분해·사람 배정·UI 프레임워크·branch 경로 미확정.
- ✅ 순환 의존 없음, 동시 수정 위험 회피용 계약 우선 고정 지점 명시(NFR-INT-1).
- ✅ Mermaid + 텍스트 대안 포함(content-validation).

---

## 7. 다음 단계 (제안)

**Units Generation** — 위 컴포넌트·계약을 근거로 **실제 Unit 경계·Unit 간 의존성·Unit↔스토리 매핑·병렬화·사람별 배정**을 결정. (컴포넌트 9개/서비스 3개는 그대로 Unit이 되지 않을 수 있음 — 공통 lifecycle은 통합.)

## Approved operator/org demo alignment (2026-09-09)

Existing product scope maintained. The live demonstration may select explicit team-skill-demo-20260909 on the same ddthon remote, while preserving original team-skill-store history. New live database starts with validated P0 only; P1 Cold searches it and the user approves newly discovered P1 publication. Exact human review, independent Replay and confirmed push remain required. Operator-only no-prompt viewing is environment preparation, not Agent discovery. End-of-task candidate triggers a publication permission invitation; no separate user publish request is required. No S3 adapter or general NASCA detection is claimed.

## P0 자동 재사용 승인 정정 (2026-09-09)
NFR-SEC-4의 P0 한정 예외를 C8 기존 apply-requirements 경계에 구현한다. C9는 사용자의 설치 요청과 운영자 정책을 전달만 하고 승인 값을 생성하지 않는다. C8은 실제 실패/C5 MATCH, exact content 무결성, 운영자가 고정한 workspace/source/remote/branch/exact ref, S3 게시·재사용 상태를 확인한다. C5/S1/C3 및 P1 게시 파이프라인 역할은 그대로다. 다른 원격 Skill 및 P1에는 기존 명시적 확인을 유지한다. 상세 절차/검증: construction/plans/p0-scoped-auto-reuse-code-generation-plan.md. 이전 문단의 포괄적 자동 실행 금지는 이 좁은 예외 외에서 유효하다.
