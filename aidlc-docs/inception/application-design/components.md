# Components — Agent SkillLoop

**단계**: INCEPTION / Application Design — Part 2
**작성일**: 2026-09-08
**근거**: 승인된 `requirements.md`, `stories.md`, `application-design-plan.md`(AD-Q1~Q6)

> **분석·제안**입니다. 컴포넌트는 **책임 축**으로 도출했으며 **seam (a)~(f)와 일대일 대응하지 않고, 개수를 미리 고정하지 않습니다.** 실제 **Unit 분해·사람별 배정은 Units Generation**에서 결정합니다. 상세 비즈니스 규칙은 **Functional Design(per-unit)** 에서 정의합니다.
> **공통 원칙(AD-Q5)**: 각 상태(state)는 **소유 컴포넌트만 쓰기**하고, 타 컴포넌트는 **명시적 인터페이스로만 접근**한다. 공유 mutable state 동시 수정을 최소화(NFR-INT-1)한다.

---

## 컴포넌트 개요 (책임 축)

| ID | 컴포넌트 | 계층 | 소유 상태(쓰기 주체) | 핵심 책임 | 주요 요구사항 |
|---|---|---|---|---|---|
| C1 | **SkillDescriptor** (모델) | Domain | (무상태 값객체) | 불변 content identity + 가변 usage의 **논리 분리**, digest 계산(불변 content만) | FR-SKILL-1~4 |
| C2 | **SkillStore** | Persistence | 로컬 Skill content 저장 | 영속화·dedup·무결성·CONFLICT 판정·import/export 계약·재시작 보존 | FR-SYNC-3, NFR-RES-1/2/4 |
| C3 | **UsageTracker** | Persistence | usage 이력·카운트 | 실제 성공 식별·`actual_reuse` 집계·중복 집계 방지·DEMO_SEED 구분. **digest 불변** | FR-USAGE-1~3 |
| C4 | **GitSyncAdapter** | Sync | (원격 전송만) | private Git clone/pull/push **전송 전담**. store의 import/export **위에서** 동작 | FR-SYNC-1/2/4 |
| C5 | **SkillSearchMatcher** | Capability | (무상태) | 결정적 키워드·태그 검색 + applicability 확인 + 매칭 근거 | FR-MATCH-1~3 |
| C6 | **ReplayVerifier** | Capability | (실행 결과 산출) | 후보의 **독립 Replay** 실행 → 실제 `PASS`/`FAIL`/`NOT_RUN` 산출 | FR-P1-7(검증) |
| C7 | **EnvHarness** | Capability | 합성 환경 픽스처 | 통제된 합성 환경 **준비만**(P0 이중 mock index, P1 보호 XLSX + read-only 표면). 실패/성공은 실제 실행 관찰로 드러남, 정답 절차 공급·강제 raise 안 함 | FR-P0-2, FR-P1-1 |
| C8 | **CLI** | Surface | (오케스트레이션 진입점) | 핵심 명령 제공·사람 단독 재현. 서비스 계층 호출 | FR-SURF-2/3 |
| C9 | **AgentSkillWrapper** | Surface | (없음) | 자연어 요청 → CLI 호출 **얇은 wrapper**. 로직 중복 금지 | FR-SURF-1, NFR-SEC-4 |
| C10 | **OrgAggregator** (집계 read-model) | Capability | (없음 — 읽기 전용 파생) | 로컬 store·usage + 공유(import된) 데이터로 **단일 조직 스냅샷** 산출. 소유 상태 미수정 | FR-ORG-1~5, FR-USAGE-4, FR-UI-3 |
| C11 | **StatuslineRenderer** | Surface | (없음) | C10 스냅샷 → 상태줄 간단 표시 | FR-UI-1, FR-UI-3 |
| C12 | **DashboardServer** (로컬 읽기전용) | Surface | (없음) | C10 스냅샷 → localhost 읽기전용 대시보드 | FR-UI-2, FR-UI-3, NFR-SEC-2 |

> 서비스(오케스트레이션) 계층 S1~S3은 `services.md` 참조. C1~C12의 개수는 **제안**이며 Units에서 통합/분할될 수 있다(예: C2·C3는 공통 lifecycle이면 한 Unit으로 묶일 수 있고, C10~C12는 "조회·집계·표현" Unit으로 묶일 수 있음 — AD-Q1의 "공통 lifecycle 과도 분할 금지"). **C10~C12는 읽기전용 파생 표면**이며 게시 게이트·usage 쓰기·저장 상태를 소유하지 않는다.
>
> **범위 변경(UI+Git) 반영 요약**: C10/C11/C12는 신규 표면·집계 read-model. C3 UsageTracker에 **공유 재사용 이력 export/import(이벤트 dedup)** 책임 추가, C4 GitSyncAdapter는 **동일 저장소 `team-skill-store` branch**를 대상으로 하고 **descriptor + 비민감 재사용 이력만** 전송(로컬 DB 파일 미전달, FR-SYNC-5). 상세는 아래 및 `component-methods.md`.

---

## 컴포넌트 상세

### C1 — SkillDescriptor (도메인 모델)
- **목적**: 하나의 Skill을 단일 구조화 descriptor로 표현하되 **불변 content identity**(`id`, `version`, `digest`, `origin`, `applicability`, `procedure`)와 **가변 usage**(`actual_reuse`, `DEMO_SEED`)를 **논리적으로 분리**(AD-Q2).
- **책임**: (a) content 직렬화/역직렬화(round-trip), (b) **불변 content에 대해서만** digest 계산(FR-SKILL-4), (c) usage 변경이 digest에 영향을 주지 않음을 보장.
- **인터페이스**: `content_view`(읽기·digest 대상) / `usage_view`(조회) 를 구분 노출. 실행 스크립트 미포함(서술적 procedure만).
- **불변식(PBT 대상)**: 직렬화 round-trip 동일성, 동일 content→동일 digest, usage 변경→digest 불변.

### C2 — SkillStore (로컬 저장)
- **목적**: 로컬 Skill content의 **유일한 writer**. 무결성·중복·충돌·저장의 책임 소재(AD-Q4).
- **책임**: (a) content 저장/조회, (b) **dedup**(digest 기반, NFR-RES-1), (c) **CONFLICT 판정**(동일 `(id, version)`에 상이 digest만 — FR-SYNC-3/NFR-RES-2), (d) **import/export 계약**(GitSyncAdapter가 이 계약 위에서 동작), (e) 재시작 보존(NFR-RES-4).
- **경계**: 원격에서 받은 **상태 문자열만으로 검증 완료를 인정하지 않는다**(게시 판단은 PublishPipeline). sync가 저장 파일을 직접 수정하지 않는다.

### C3 — UsageTracker (사용 실적)
- **목적**: 가변 usage의 **append 전용** 관리(AD-Q2 인터페이스 분리). 별도 DB는 두지 않으며(SkillStore와 동일 영속 lifecycle 공유 가능 — Units 결정) content digest에 영향 없음.
- **책임**: (a) **검증된 실제 성공만** `actual_reuse += 1`(FR-USAGE-1), (b) 실패·검색·Replay·retry·**sync·restart 중복 집계 방지**(FR-USAGE-2, AD-Q5), (c) `DEMO_SEED`(합성)와 실제 증가분 **구분 표시**(FR-USAGE-3).
- **범위 변경(공유 재사용 이력)**: (d) **재사용 이벤트를 이벤트 식별자를 가진 레코드로 관리**하고, **VERIFIED_REUSE**(정확한 Skill 참조 + 실제 성공 근거 + 비-DEMO) 자격으로 **export/import**한다(비민감·합성만). (e) import 시 **정확한 Skill 참조·실제 성공 근거를 검증**하고 **이벤트 식별자 기준 dedup**으로 중복 집계(+1 중복)를 방지한다(FR-USAGE-4, FR-ORG-3). (f) `DEMO_SEED`는 실제 실적으로 집계하지 않는다. — 저장 상태의 유일 writer는 여전히 C3.
- **자격 구분(범위 변경 정정)**: 재사용 이벤트 공유 자격(**VERIFIED_REUSE**)은 **신규 Skill 게시 게이트(SHAREABLE=사람 승인+독립 Replay PASS+digest 동일성)와 별개**다. import 한 남의 게시 Skill 을 **실제 재사용만** 한 환경도 그 Skill 을 다시 후보화·승인·Replay 하지 않고 자기 실적 이벤트를 공유할 수 있다(A게시→B import→B 검증 성공→B 이벤트 공유→A가 조직 실적에 1회 반영). 신규 Skill 게시 게이트는 그대로 유지.

### C4 — GitSyncAdapter (원격 동기화)
- **목적**: Git 공유 대상과의 **전송 전담**(clone/pull/push). 별도 서버 없음(FR-SYNC-2). **SKIP-BOUNDARY-2**: 원격 sync 요구 유지(로컬 Git만으로 축소 아님).
- **범위 변경(대상·전송 내용)**: 이번 시연의 대상은 **동일 저장소 `THEGREATCJPark/ddthon`의 `team-skill-store` branch**(별도 저장소도 동일 의미로 허용). 전송 내용은 **공유 가능한 descriptor + 비민감 재사용 이력 레코드**뿐이며 **로컬 DB 파일 자체는 전송하지 않는다**(FR-SYNC-5). **last-sync 메타(시각·branch revision)**를 store/aggregator가 조회할 수 있도록 남긴다(FR-ORG-5). 실제 branch·Git 경로·세부 운용은 **미결정**(Units 담당 확정 후 초기 구현 준비).
- **책임**: (a) 원격 push/pull, (b) 전송 실패(네트워크·인증) 시 **로컬 상태 미손상**·명확한 오류·재시도 가능 상태(FR-SYNC-4/NFR-RES-3).
- **경계**: 무결성·CONFLICT·dedup·저장은 **SkillStore 책임**이며 여기서 재구현하지 않는다. 공유 재사용 이력의 이벤트 dedup은 **UsageTracker 책임**이다. **승인·게시 lifecycle을 구현하지 않는다**(PublishPipeline 책임). 원격 상태 문자열만으로 로컬 승인·Replay·실적을 만들어내지 않는다(AD-Q4).

### C5 — SkillSearchMatcher (검색·매칭)
- **목적**: 결정적 검색으로 후보 목록 생성 + 현재 문제 적용 가능성 판정.
- **책임**: (a) 키워드·태그 검색(FR-MATCH-1), (b) **applicability 확인**(FR-MATCH-2), (c) 매칭 근거(키워드/조건) 제시(FR-MATCH-3), (d) 검색 **미호출·오류·timeout을 `NO_MATCH`와 구분**되는 상태로 반환(FR-P1-2).

### C6 — ReplayVerifier (독립 검증)
- **목적**: 후보 Skill을 **독립적으로 재실행**해 실제 효과를 판정.
- **책임**: exact candidate(content/version/digest)에 대해 Replay 실행 → `PASS`/`FAIL`/`NOT_RUN` 산출. 결과는 **화면 문구가 아닌 실제 효과**(NFR-TEST-2). PublishPipeline이 이 결과를 게이트 입력으로 사용.

### C7 — EnvHarness (합성 환경 **준비만**)
- **목적**: 외부 인터넷·실제 회사 데이터·DRM 없이 통제된 환경을 **구성**한다(CON-1).
- **책임**: (a) **P0**: 공개 모의 index(대상 패키지 없음)+허용 사내 모의 index(무해 wheel) 구성(FR-P0-2), (b) **P1**: 보호 속성 합성 XLSX + Windows read-only 표면을 **배치**한다(NFR-SEC-2).
- **경계(변경)**: 실패/성공은 **환경 사실**이며 **실제 parser 실행 결과를 관찰**해 드러난다. EnvHarness는 (i) 직접 접근 실패를 **강제 raise 하지 않고**, (ii) **정답 대안 절차를 공급해 Agent가 선택만 하게 하지 않는다.** 무엇이 존재/허용되는지의 **사실만** 제공한다. **탐색·대안 선택·코드 작성·실행은 실제 업무 Agent의 책임**(FR-P1-1/4).

### C8 — CLI (제품 표면)
- **목적**: 핵심 기능을 **사람이 단독 재현** 가능한 명령으로 제공(FR-SURF-2/3).
- **책임**: 인자 파싱 → **서비스 계층(S1~S3) 호출** → 결과·상태 출력. 명령 동사(예: search/apply/record/propose/review/replay/publish/sync)의 **최종 집합은 Functional Design에서 확정**.
- **경계**: 검증·카운트·게시 판단을 CLI에 **중복 구현하지 않는다**(서비스 위임). 게시 게이트를 **우회하지 않는다**(AD-Q3).

### C9 — AgentSkillWrapper (Claude Code Skill)
- **목적**: 자연어 요청을 **CLI 호출로 연결**하는 얇은 wrapper(AD-Q6).
- **책임**: 요청 해석 → 해당 CLI 명령 실행. **핵심 제품 로직/판단을 담지 않는다**. NFR-SEC-4를 표면에서도 준수한다. P0의 사용자 요청·운영자 exact 범위 검증은 C8에서 수행하며 허용된 경우 추가 질문 없이 명시적 CLI 호출로 진행한다. P1 확인은 유지한다.
- **경계(명확화)**: "얇은 wrapper"는 **제품 로직 중복 금지**이지 **Agent 탐색 역할 제거가 아니다.** P1의 환경 관찰·허용 대안 선택·코드 작성·실행은 **Agent가 수행**하며 CLI 명령으로 연결된다. (Agent=탐색·실행 주체 / CLI·서비스=재현 가능한 제품 로직·검증·상태 / Wrapper=연결)

### C10 — OrgAggregator (집계 read-model, 범위 변경 신규)
- **목적**: 상태줄·대시보드가 공유하는 **단일 조직 스냅샷**을 산출한다(FR-UI-3, 두 화면 동일 기준).
- **책임**: (a) 로컬 `SkillStore`(공유 게시된 것) + `UsageTracker`(실제 재사용 이력, 공유 import 포함)에서 **읽기 전용**으로 집계, (b) 공유 게시 Skill을 **중복·버전 구분**(digest·`(id,version)`)해 수 산출(FR-ORG-1), (c) **작성자(origin)·재사용자(alias) 식별과 팀원별 기여·재사용** 집계(FR-ORG-2), (d) **로컬 후보/검토/게시대기 vs 원격 공유 완료(PUBLISHED)** 구분(FR-ORG-4) — 이 상태는 **S3 의 읽기전용 상태 조회 계약(`list_lifecycle_states`/`query_lifecycle_state`)으로만 조회**하고 **추정하거나 게이트를 재구현하지 않는다**, (e) **인기 랭킹**(실제 검증 재사용 기준)과 **최근 활동**, (f) **last-sync 메타(시각·revision)와 조회 가능 데이터 범위**(FR-ORG-5), (g) 실제 실적/`DEMO_SEED` 구분(FR-USAGE-3).
- **경계**: **소유 상태를 쓰지 않는 읽기전용 파생**. 게시 판단·usage 쓰기·저장·sync를 수행하지 않으며 상태 소유자(S3)에게 조회만 한다. 원격에서 import 한 게시본은 `remote_publish_evidence`(원격 게시 근거)와 `local_review_evidence`(수신 환경 검토 상태)를 **분리 표시**하고, **수신 환경의 승인·Replay 기록을 만들어내지 않는다**(AD-Q4). secret·원본 업무 데이터를 스냅샷에 포함하지 않는다(NFR-SEC-1).

### C11 — StatuslineRenderer (상태줄, 범위 변경 신규)
- **목적**: C10 스냅샷을 받아 상태줄에 **간단히** 표시(FR-UI-1). 조직 Skill 수·내 기여·인기 Skill·재사용 현황, 실적/`DEMO_SEED` 구분.
- **경계**: 표시 전용. 집계 로직·상태 변경 없음. 대시보드와 **동일 스냅샷**(FR-UI-3).

### C12 — DashboardServer (로컬 읽기전용 대시보드, 범위 변경 신규)
- **목적**: C10 스냅샷을 localhost **읽기전용** 화면으로 제공(FR-UI-2). 조직 요약·Skill 목록/검색/상세·기여/재사용·검토/Replay/게시 상태·최근 활동·last-sync.
- **경계**: **쓰기·승인·게시 액션 없음**(NFR-SEC-2). 인증·호스팅·멀티유저 서버 범위 외. UI 근거는 사용자 승인 FR-UI/FR-ORG이며 특정 외부 구현 코드·backend 구조에 의존하지 않는다. UI 프레임워크·표시 방식 **미결정**(Functional Design/Code Generation).

---

## 요구사항 ↔ 컴포넌트 추적성 (요약)

| 요구사항 영역 | 담당 컴포넌트 |
|---|---|
| Skill 표현·무결성 (FR-SKILL) | C1, C2 |
| 사용 실적 (FR-USAGE-1~3) | C3 |
| 공유 재사용 이력·집계 (FR-USAGE-4) | C3(VERIFIED_REUSE export/import·검증·이벤트 dedup, 게시와 독립) → C10 |
| 원격 동기화 (FR-SYNC, branch 대상) | C4(push_descriptors/push_shared_usage/pull; +C2 무결성/충돌, +C3 이벤트 검증·dedup) |
| 검색·매칭 (FR-MATCH) | C5 |
| P0 재사용 (FR-P0) | S1 ← C5, C7, C2/C3 |
| P1 업무·후보화 (FR-P1-1~6) | S2 ← C5, C7, C1 |
| 검토·Replay·게시 (FR-P1-7) | S3 ← C6, C2, C4.push_descriptors (+ 읽기전용 상태 조회 계약 제공) |
| 조직 집계 (FR-ORG-1~5) | C10 ← C2, C3, C4(last-sync), **S3 상태 조회(읽기전용)** |
| UI 표면 (FR-UI-1~3) | C11(상태줄), C12(대시보드) ← C10 |
| 제품 표면 (FR-SURF) | C8, C9 |
| 통합 위험 (NFR-INT-1) | 전 컴포넌트 소유 경계 원칙 (C10~C12는 읽기전용 파생) |
