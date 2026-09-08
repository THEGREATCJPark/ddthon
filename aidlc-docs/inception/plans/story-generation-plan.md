# Story Generation Plan — Agent SkillLoop (User Stories Part 1)

**단계**: INCEPTION / User Stories — Part 1 (Planning)
**깊이**: minimal
**작성일**: 2026-09-08
**상태**: ✅ **승인됨 (2026-09-08)** — Q-A=A, Q-B=A, Q-C=A, Q-D=A. Part 2(stories.md/personas.md) 생성 근거.
**근거**: 승인된 `requirements.md`(FR/NFR ID), `user-stories-assessment.md`(EXECUTE-minimal), `execution-plan.md`

> 이 계획은 **어떤 persona/스토리를 어떤 형식으로 생성할지**를 정하고 최소 질문을 확인받는 문서다. **Unit 수·담당자·아키텍처·schema/API는 확정하지 않는다.** seam (a)~(f)는 후보로만 유지한다.
> 아래 **질문에 `[Answer]:` 태그로 답**해 주세요. 맞는 게 없으면 **X) Other**에 직접 적어 주세요. 승인(계획 확정) 전에는 Part 2(스토리 생성)로 넘어가지 않습니다.

---

## 1. 계획 개요

- **목표 산출물(Part 2)**: `user-stories/stories.md`(INVEST), `user-stories/personas.md`.
- **분량 원칙**: **minimal** — 기존 FR ID를 참조하고 요구사항 원문을 복제하지 않는다. 카운트(§4.6)·거절·미실행(NO_MATCH/NOT_RUN/FAIL)·게시 게이트(FR-P1-7) 조건은 **관련 스토리의 수용 기준에 접어 넣어** 중복을 줄인다.
- **경계**: 새 기능/NFR/clarification 추가 금지. 스토리는 승인된 요구사항의 재표현·수용 기준화에 한정.

---

## 2. 제안 Persona (초안 — 질문 Q-B에서 조정)

| ID | Persona | 유형 | 근거(requirements §2) |
|---|---|---|---|
| PER-1 | **코딩 경험이 적은 사내 엔지니어** (Coding Agent로 데이터 분석·업무 자동화) | Primary | §2 Primary User |
| PER-2 | **팀 리뷰어** (새 Skill 후보 검토·승인/거절) | 이해관계자 | §2 이해관계자 (2) |
| PER-3 | **다음 Agent / 재사용자** (검증된 Skill을 재사용) | 이해관계자 | §2 이해관계자 (3) |

> (개발자/팀은 PER-1/PER-3에 흡수 가능 — Q-B에서 별도 분리 여부 확인.)

---

## 3. 제안 스토리 목록 (초안 — FR ID 참조, minimal)

> 각 스토리는 Part 2에서 수용 기준을 붙인다. 아래는 **범위·매핑 초안**이며 질문 응답 후 확정.

**P0 — 기존 Skill 재사용**

- **US-P0-1** (PER-1/PER-3): 자연어로 `requirements.txt` 설치를 요청하면, 검증된 Team Skill을 검색·적용해 **실제 설치 성공·검증**되고 재사용 실적이 정직하게 +1 된다. → FR-SURF-1~3, FR-P0-1~4, FR-MATCH-1~3, FR-USAGE-1~3
  - (수용 기준에 접어 넣을 조건: 이중 mock index 재현, applicability 확인, actual_reuse만 +1·DEMO_SEED 구분)

**P1 — 새 경험 축적 loop**

- **US-P1-1** (PER-1): 보호 XLSX 직접 접근이 **실제 실패**하고, Team Skill/Org Knowledge를 **실제 검색**한 뒤 적용 가능한 것이 없을 때만 `NO_MATCH`로 진행한다(검색 미호출/오류/timeout은 NO_MATCH 아님). → FR-P1-1, FR-P1-2
- **US-P1-2** (PER-1): 환경 사실을 확인(대화형)하고 **허용된 read-only 대안 절차**를 찾아 파일 내용을 얻어 **업무를 완료**한다(3개월 → OLS → 다음 달 예측, 실제3+예상1 구분 표시). → FR-P1-3, FR-P1-4, FR-P1-5
- **US-P1-3** (PER-1): 업무 계산법이 아니라 **환경 접근 절차만** 새 Skill 후보로 만든다(계산식·값·차트 로직 제외). → FR-P1-6, NFR-SEC-1
- **US-P1-4** (PER-2): 후보를 **사람이 검토(승인/거절)**하고 **독립 Replay**를 실행하며, **게시 게이트 조건이 모두 충족될 때만 private Git 저장소에 게시**된다(FAIL/NOT_RUN/미완료 게시 금지, 승인 후 내용 변경 시 재검토·재Replay). → FR-P1-7, FR-SYNC-1~4, NFR-RES-2

**교차(수용 기준으로 흡수 후보 — 별도 스토리로 세우지 않음)**

- 무결성/충돌/재시작 보존(NFR-RES-1~4), 원격 자동 실행 금지(NFR-SEC-4), 통합 위험(NFR-INT-1)은 관련 스토리의 수용 기준·비기능 제약으로 참조.

---

## 4. 확인 질문 (최소)

### Q-A — 스토리 분해 세분화
스토리를 어느 정도로 나눌까요?

A) **위 초안 그대로 — P0 1개 + P1 4개(총 5개)** (Recommended) — minimal 원칙에 맞고 흐름 단계를 그대로 반영

B) 더 통합 — P0 1개 + P1 2개(탐색·완료 / 검토·게시)로 축약(총 3개)

C) 더 세분화 — P1의 검토·Replay·게시를 각각 분리(총 6개 이상)

X) Other (please describe after [Answer]: tag below)

[Answer]: A — P0 1개 + P1 4개(총 5개). private Git 원격 동기화도 관련 스토리 수용 기준에 FR-SYNC ID로 연결해 누락 방지.

### Q-B — Persona 세분화
persona를 몇 개로 둘까요?

A) **PER-1(Primary) + PER-2(리뷰어) + PER-3(다음 Agent/재사용자) = 3개** (Recommended) — 요구사항 §2와 정합, 최소

B) PER-1 + PER-2 = 2개 (재사용자는 PER-1에 흡수)

C) 위 3개 + "개발자/팀"을 별도 persona로 분리 = 4개

X) Other (please describe after [Answer]: tag below)

[Answer]: A — 3개(PER-1 사내 엔지니어[Primary], PER-2 팀 리뷰어, PER-3 다음 Agent 재사용자). **Agent는 업무 수행 주체로 명시.**

### Q-C — 수용 기준 형식
스토리 수용 기준을 어떤 형식으로 쓸까요?

A) **Given/When/Then(GWT) + 각 기준에 관련 FR ID 태그** (Recommended) — 검증 가능·추적 가능, Build & Test와 연결 쉬움

B) 체크리스트 형식(불릿) + FR ID 태그

X) Other (please describe after [Answer]: tag below)

[Answer]: A — Given/When/Then + FR ID 태그. 실제 성공·실패 판정 가능하게 간결히, 요구사항 설명 반복 금지.

### Q-D — 카운트/거절/미실행 조건의 위치
카운트(§4.6)·거절·NO_MATCH·NOT_RUN·게시 게이트 조건을 어디에 둘까요?

A) **관련 스토리의 수용 기준에 접어 넣어 중복 최소화** (Recommended) — 사용자 요청(중복 감소)과 정합

B) 별도의 "규칙/제약" 절로 한 번에 모아 정리

X) Other (please describe after [Answer]: tag below)

[Answer]: A — 관련 스토리 수용 기준에 포함. 실제 reuse·DEMO_SEED 구분, 중복 집계 방지, 거절·보류·Replay 실패/미실행 시 게시 금지를 해당 흐름에 연결.

---

## 5. 계획 승인 후 진행 (Part 2 예정)

계획 확정 시: `stories.md`(INVEST, 위 응답 반영) + `personas.md`(최소)를 생성하고 **REVIEW REQUIRED**에서 정지한다. Unit/역할/아키텍처는 계속 미확정 유지.

---

## ⛔ REVIEW REQUIRED
위 **Q-A ~ Q-D에 답**해 주시면 계획을 확정하고 Part 2(스토리 생성)로 진행합니다. 답변 전에는 스토리를 생성하지 않습니다.
