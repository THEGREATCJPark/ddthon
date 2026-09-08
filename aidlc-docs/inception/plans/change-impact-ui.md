# 변경 영향 분석 — UI + Git 공유 방식 통합 변경안

**단계**: INCEPTION (범위 변경 재검토) — 승인 대기
**작성일**: 2026-09-08 (개정: UI+Git 통합)
**유형**: **사용자 요청 범위 변경(Scope Change)** — (A) 상태줄 + 로컬 읽기전용 웹 대시보드, (B) Git 공유 방식 변경
**상태**: **✅ 승인·반영 완료 (2026-09-08, SCOPE-CHANGE-1)** — §8 최소 반영을 requirements/stories/personas/execution-plan/application-design/aidlc-state에 적용함. 이 문서는 변경 근거·영향 이력으로 보존한다. (export **SHAREABLE** 정정 유지.) Application Design 전체 승인·Units Generation은 반영본 재검토 후 결정.

> **불변 제약**: 기존 P0/P1 완료 범위 유지. **Unit·담당자·프레임워크·branch/Git 경로 선결정 금지.** 과거 Q3 답변·기존 승인 이력 **보존**, 이번 변경은 **별도 기록**. 원격 clone/pull/push·무결성·충돌·실패 시 로컬 보존 요구 **유지**.

---

## 0. 참고 저장소(ttt) 확인 — **정정** (source 확인, 렌더링 미확인)

> **이후 provenance 적용 범위**: 아래 외부 관찰은 과거 UI scope change 검토 이력으로 보존한다. 이후 구현 근거는 사용자 승인 FR-UI/FR-ORG와 현재 ddthon의 승인 AI-DLC 산출물·실제 실행 증거이며, 아래 내용은 외부 사전 구현의 재접근·코드/backend 채택·완료 증거 사용 지시가 아니다. 사용자 별도 승인 전 외부 사전 구현 Reference 접근을 중단한다. 기존 범위 변경 승인 및 현재 Application Design REVIEW REQUIRED 위치는 유지한다.

- **정정**: 이전 "웹 대시보드 없음"은 **오류**. `core/skillloop/organization.html`에 **웹 대시보드 소스가 존재**한다(WebFetch로 소스 확인, 2026-09-08). **소스 확인과 실제 렌더링 확인은 구분**한다(렌더링은 미확인).
- **확인된 화면 구성(표현 참고 대상)**: 헤더/툴바(새로고침 "최신 기록 확인", sync 상태 `연결 중…`, revision), **요약 카드 4개**(공개된 Skill=서로 다른 Skill 기준 / 검증된 재사용=수동 승인 / 재사용자 alias / 기여자 alias), **Skill 목록·검색**(이름·작성자·설명 필터, 열: Skill/적용정보·검증근거·재사용; 상세: version·digest·applicability/procedure step 수·status·quality stage·Replay 성공/실패 수·검증 재사용 수·unique alias 수), **기여/재사용 표**(기여자·공개 Skill·다른 alias 재사용·재현/검토), **최근 활동**(행위자·종류·상세·시각·Case 근거 링크), **정책 푸터**(counting_policy: 검색·새로고침·replay·QA는 카운트 제외).
- **데이터 출처(중요)**: 값은 **하드코딩이 아님** — JS가 `fetch('/api/organization')`로 **런타임 조직 집계 API**에서 받아 5초마다 갱신. 즉 **ttt는 조직 전체 현황을 중앙 API로 집계**한다. → 본 제품은 **백엔드 구조(중앙 API)를 채택하지 않으므로**(사용자 지시), **동일 지표를 Git 공유 데이터로부터 집계하는 계약을 별도로 설계**해야 한다(§3에서 상세). **표현(카드·표·상태 라벨)만 참고**, 서버 구조 미채택.

---

## A. UI 변경 (상태줄 + 로컬 읽기전용 대시보드)

### A.1 영향 문단 · 최소 반영안(제안)
- **Requirements**: `FR-UI-1`(Claude 상태줄 — 조직 Skill 수·내 기여·인기 Skill·재사용 현황 간단 표시), `FR-UI-2`(**로컬 브라우저 읽기전용** 대시보드 — 조직 요약 카드·Skill 목록/검색/상세·기여/재사용·검토/Replay/게시 상태·최근 활동), `FR-UI-3`(두 화면 **동일 집계 기준** + **DEMO_SEED ↔ 실제 검증 실적 구분**, FR-USAGE-3 재사용). 범위 주의: **읽기전용**(승인·게시·쓰기 액션 없음), **localhost 시연**, 인증/호스팅/멀티유저 서버 범위 외.
- **User Stories**: `US-UI-1`(상태줄), `US-UI-2`(대시보드) 최소 추가. 수용 기준에 동일 집계·DEMO 구분·읽기전용·상태 라벨 매핑 흡수.
- **실행 계획**: 병렬 seam `(g) 조회 계약 + 집계 read-model + 표현 표면(상태줄/대시보드)` 후보 추가.
- **Application Design**: **집계 Read-Model**(읽기전용, 소유 상태 미수정) + **표현 표면 2개**(상태줄 렌더러, 로컬 대시보드 뷰). 컴포넌트 수는 유연(억지 유지 안 함).

---

## B. Git 공유 방식 변경 (별도 private 저장소 → 동일 저장소 branch)

### B.1 변경 내용(제안 설계안)
- **기존 전제(Q3=A)**: "**별도 private Git 저장소**"에 검증된 Team Skill 저장(FR-SYNC-1, ASSUMPTION-1).
- **변경 제안**: 이번 시연(합성·비민감 데이터)에서 **단일 저장소 다중 branch** 구조 우선 검토:
  - **`THEGREATCJPark/ddthon` `main`**: 제품 소스 · AI-DLC 산출물(`aidlc-docs/` 전체) · 실행 안내 · 시연 증거.
  - **동일 저장소 `team-skill-store` branch**: **공유 가능한 Skill descriptor + 필요한 재사용 이력**(공유 게시 대상만).
  - **각 실행 환경의 로컬 저장 상태는 유지**하고, **DB 파일 자체를 Git으로 전달하지 않는다**(descriptor/이력 레코드만 공유).
- **동기**: public 제출이 공유 저장소 공개를 강제해서가 아니라 **시연 설정 부담 축소를 위한 사용자 선택**.
- **유지 요구**: 원격 clone/pull/push · 무결성(digest) 검증 · CONFLICT 처리(동일 (id,version)+상이 digest) · 실패 시 로컬 보존. **SHAREABLE 정정 유지**(§6).

### B.2 승인된 항목 영향
| 항목 | 현재 | 변경 영향(제안) |
|---|---|---|
| **FR-SYNC-1** | "별도 private 저장소" | "**공유 저장소의 전용 branch(team-skill-store)** 또는 별도 저장소" 로 일반화. transport 의미(clone/pull/push)·무결성·충돌·실패 보존은 불변. |
| **FR-SYNC-2/3/4, NFR-RES-1~3** | 무결성/충돌/실패 보존 | **불변**(대상이 branch로 바뀔 뿐). |
| **FR-P1-7 게시** | "private Git 저장소에 게시" | 게시 대상 = **team-skill-store branch**. 게시 게이트·SHAREABLE·PUBLISHED/PUBLISH_PENDING 구분 **불변**. |
| **ASSUMPTION-1** | "시연용 별도(합성) 저장소" | "**동일 저장소 team-skill-store branch**(합성·비민감)" 로 갱신. |
| **CON-2** | public GitHub 제출 | **정합**(같은 저장소 사용). 단 branch에 **secret·원본 데이터 비포함**(NFR-SEC-1) — 공유 대상은 descriptor + 비민감 재사용 이력만. |
| **DB 파일** | (암묵) | **Git 미전달 명시**(로컬 상태 보존, NFR-RES-4). |
| **Stories US-P1-4 AC-5** | private Git 원격 | branch 대상으로 문구 조정(FR-SYNC 참조 유지). |
| **App Design C4 GitSyncAdapter** | 원격 저장소 전송 | **branch 대상 push/pull**. store import/export 계약 위 동작·게시 lifecycle 미구현 **불변**. |
| **Q3 이력** | Q3=A 승인 | **보존**. 이번 변경은 별도 change 기록(본 문서 + audit). |

---

## 3. "조직 현황을 기존 계약으로 제공 가능" 판단 — **보완(정정)**

**결론: 로컬 `SkillStore.list()` + `UsageTracker.get_usage()`만으로는 조직 전체 현황을 제공할 수 없다.** ttt도 중앙 API로 집계함(§0). Git-branch 공유를 택했으므로 **공유 데이터 기반 집계 계약**이 필요하다. 각 항목의 충족 여부:

| 화면이 요구하는 조직 집계 | 기존 계약만으로? | 필요한 추가 계약/작업 |
|---|---|---|
| 여러 환경 수신 Skill의 **중복·버전 구분** 공유 게시 Skill 수 | ❌ | branch에서 pull → **dedup(digest) + (id,version) 구분** 집계. import 계약에 이미 dedup/CONFLICT 있으나 **"공유 게시된 것"만 세는 view 기준** 추가 필요. |
| **작성자·재사용자 식별 기준** + 팀원별 기여 집계 | ❌(부분) | **identity 기준 정의**(작성자=origin, 재사용자=alias). 팀원별 기여/재사용 집계 규칙 추가. |
| **다른 환경의 실제 재사용 이력 전달** + 재동기화 시 **중복 집계 방지** | ❌ | **usage 이력의 공유 export/import 계약 신설**: 공유 가능한 실제 재사용 레코드(이벤트 id·alias·evidence)를 branch에 반영, **재sync 시 이벤트 id 기준 dedup**(중복 +1 금지). DEMO_SEED는 실제로 집계하지 않음. |
| **로컬 후보/검토/게시대기** vs **원격 공유 완료** 구분 | ⚠️(부분) | S3 상태(LOCALLY_APPROVED/PUBLISH_PENDING vs PUBLISHED)로 구분 가능하나, **"원격 공유 완료" = branch push 성공 확인** 기준을 집계 view에 명시. |
| **마지막 동기화 기준 + 현재 조회 가능 데이터 범위** | ❌ | **last-sync 메타(시각·branch revision) 계약 신설**. 화면은 "이 스냅샷은 마지막 sync 기준"임을 표시. |

**핵심 판단**: 화면은 **읽기전용**이지만, **조직 집계를 위해 usage 이력의 공유 동기화·import 계약 보완이 필요**하다(단순 로컬 조회로 불가). 즉:
- **기존 계약으로 가능**: 로컬 관점 수치(내 로컬 Skill·내 usage), Skill 상세 필드, 로컬 상태 라벨.
- **추가 작업 필요**: (a) **공유 usage 이력 export/import + 이벤트 기준 dedup**, (b) **identity/기여 집계 기준**, (c) **인기 랭킹 기준**(실제 검증 재사용 기준 정렬), (d) **last-sync 메타·데이터 범위 표시**, (e) 집계 **Read-Model 계약**(두 화면 동일 스냅샷).
- **실적 구분 원칙**: **합성 환경에서 실제 검증한 재사용 = 실제 실적**, **미리 적재한 이력 = DEMO_SEED**. 집계·화면 모두 이 구분 유지(FR-USAGE-1/3).
- **보안**: 공유 usage 이력은 **비민감·합성**만, 원본 업무 데이터·secret 비포함(NFR-SEC-1).

---

## 4. 일정 · 단계 판단 — **보완**

- **UI 착수 시점(정정)**: UI 전체를 P0 안정화 이후로 **고정하지 않는다.** **공통 조회 계약(집계 Read-Model + 공유 usage import/last-sync 메타)이 확정되면 화면 작업을 코어와 병렬** 진행.
- **선행 조건(명시)**:
  1. **화면 골격(정적 view)**: 조회 계약 초안만 있으면 코어와 병렬 착수 가능(모의 스냅샷으로 렌더).
  2. **실제 데이터 연결**: SkillStore/UsageTracker + **공유 usage import·dedup·last-sync 메타 계약 확정** 이후.
  3. **시연 검증**: team-skill-store branch에 **실제 게시(SHAREABLE→push 성공=PUBLISHED)** + 다른 환경 pull로 **조직 집계가 실제로 반영**됨을 확인한 이후. (미확인은 NOT_RUN)
- **P0/P1 완료 범위 유지.** 시간 초과 시 상태줄 우선, 대시보드 항목 축소는 별도 approval, 미완료는 PARTIAL/NOT_RUN(RISK-1 원칙).
- **NFR/Infra Design 재확인(Git 변경 포함)**:
  - **Infrastructure Design = SKIP 유지**. 근거: 로컬 읽기전용 표시 + **동일 저장소 branch 사용(신규 인프라 없음)**. 경계: 로컬 표시 방식·branch 운용은 배포/호스팅 아님. **실제 branch·Git 작업 경로 설정은 설계 승인 + Units 담당 확정 후 "초기 구현 준비"에 배치**.
  - **NFR Design = SKIP 유지**. 근거: 항목 소수, Functional Design 흡수 적절. 단 SKIP-BOUNDARY-1 확장: 읽기전용(NFR-SEC-2)·비밀/원본 비표시(NFR-SEC-1)·동일 집계/DEMO 구분(FR-UI-3)·**공유 usage dedup·중복집계 방지**·read-model 읽기전용(NFR-INT-1)을 해당 Unit 설계·테스트에 반영.
  - **NFR Requirements(minimal) 적용 확대**: 실행 계획에 이미 있는 per-unit NFR Requirements(minimal)를 **UI·동기화 Unit에도** 필요한 범위로 적용(집계 일관성·공유 usage dedup·스냅샷 갱신·읽기전용 경계). PBT-09 framework는 순수·불변 로직(직렬화/digest/dedup)에 한정 유지.

---

## 5. 화면 데이터 요약 (기존 계약 제공 vs 추가 정의)

| 항목 | 기존 계약 | 추가 정의 필요 |
|---|---|---|
| Skill 목록/검색/상세(로컬) | ✅ SkillStore/Matcher | 상세 view 필드셋 |
| 내 usage/기여(로컬) | ✅ UsageTracker | alias 식별 기준 |
| 로컬 상태(후보/검토/게시대기) | ✅ S3 상태 | 상태→라벨 매핑 |
| **조직 전체 공개 Skill 수(dedup·버전)** | ❌ | 공유 pull + 집계 view |
| **팀원별 기여/재사용** | ❌ | identity·집계 규칙 |
| **다른 환경 실제 재사용 반영** | ❌ | 공유 usage import + 이벤트 dedup |
| **인기 Skill 랭킹** | ⚠️ | 실제 검증 기준 랭킹 규칙 |
| **원격 공유 완료 vs 로컬** | ⚠️ | PUBLISHED(push 성공) 기준 view |
| **마지막 동기화·데이터 범위** | ❌ | last-sync 메타 계약 |
| 두 화면 동일 수치 | — | 단일 Read-Model 계약 |
| 로컬 표시 방식 | — | **프레임워크 미정**(설계/코드 단계) |

---

## 6. export/게시 계약 (SHAREABLE) — 유지 + 명확화

- **SHAREABLE 정정 유지**: export 대상 = **정확한 후보 사람 승인 + 독립 Replay PASS + digest 동일성**(원격 전송 완료와 무관). **최초 게시**도 SHAREABLE이므로 export 가능(순환 없음). **실패 후 재시도**도 SHAREABLE이 유지되므로 재-export/재-push 가능.
- **PUBLISHED = 원격 push(=team-skill-store branch) 성공 확인 후에만 표시.** 실패는 `PUBLISH_PENDING`(로컬 LOCALLY_APPROVED 유지 + 재시도 근거). 조직 집계 화면의 "공유 완료"는 PUBLISHED 기준.
- 반영 파일(적용 완료): `services.md`, `component-methods.md`, `component-dependency.md`, `application-design.md`.

---

## 7. 추가로 정의가 필요한 계약 (승인 시 설계에 반영 — HOW는 이후 단계)

1. **집계 Read-Model 계약**: 두 화면 동일 스냅샷(조직 요약·Skill·기여/재사용·상태·최근 활동·last-sync). 읽기전용.
2. **공유 usage export/import 계약**: 실제 재사용 이벤트(id·alias·evidence, 비민감) 공유 + **재sync 이벤트 dedup**(중복 +1 금지) + DEMO_SEED 비집계.
3. **identity 기준**: 작성자(origin)·재사용자(alias) 식별, 팀원별 집계.
4. **인기 랭킹 기준**: 실제 검증 재사용 기준 정렬·동점 규칙.
5. **last-sync 메타**: 시각·branch revision·조회 가능 데이터 범위 표시.

> 위 계약의 **구체 schema/필드/프레임워크/branch 경로는 미정**(Functional Design·Code Generation, Units 담당 확정 후).

---

## 8. 승인 시 진행할 최소 반영(영향받는 문단만)
1. `requirements.md`: FR-UI-1/2/3, FR-SYNC-1 일반화(branch 허용), FR-P1-7 게시 대상=branch, ASSUMPTION-1 갱신, CON-2 정합 주석, 공유 usage 집계 요구(FR-USAGE 확장 최소), DB 미전달 명시.
2. `stories.md`: US-UI-1/2 추가, US-P1-4 AC-5 branch 문구, 조직 집계 관련 수용 기준 최소 반영.
3. `execution-plan.md`: seam (g) + 병렬/선행 조건 + 일정 + SKIP-BOUNDARY 확장 + NFR Requirements(minimal) UI·sync Unit 적용.
4. `application-design/*`: 집계 Read-Model + 표현 표면 + 공유 usage import/last-sync 계약 반영, C4 branch 대상, 추적성 갱신.
5. `aidlc-state.md`: 범위 변경(UI+Git) 기록, NFR/Infra=SKIP 유지(근거 재확인), Q3 이력 보존 + 이번 변경 별도 기록.

**미결정 유지**: Unit·담당자·UI 프레임워크·branch/Git 경로·랭킹 세부식·집계 schema·표시 방식.

---

## ⛔ REVIEW REQUIRED
UI+Git **통합 변경 영향·최소 반영안·추가 계약·일정 영향**을 검토해 주세요.
- 🔧 **Request Changes** — 반영안/판단 수정
- ✅ **Approve (범위 변경 승인)** — §8 최소 반영을 각 문서에 적용(그 후 다시 검토 게이트)

Requirements 등 본문 적용·Application Design 전체 승인·Units Generation 진행은 **아직 아님**.
